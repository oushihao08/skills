#!/usr/bin/env python3
"""题面只读扫描；由question-prompt-scan调用。GET本机API或窄JSON输入，写新产物目录；无业务写回。"""
import argparse
import hashlib
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler


PATTERNS = [
    ('角色标记', r'<\|[^\n<>]{1,80}\|>|\[/?INST\]|(?im:^\s*(?:system|assistant|developer|tool)\s*:)'),
    ('标签', r'</?[A-Za-z_][\w:.-]*(?:\s[^<>\n]*)?/?>'),
    ('尖括号包装', r'<[^<>\n]{0,120}>'),
    ('代码围栏', r'(?m:^\s*(?:`{3,}|~{3,})[^\n]*)'),
    ('Markdown标题', r'(?m:^\s{0,3}#{1,6}\s+[^\n]+)'),
    ('Markdown强调', r'\*\*[^\n*]+\*\*|__[^\n_]+__|`[^\n`]+`'),
    ('Markdown其他包装', r'(?m:^\s*(?:={3,}|-{3,}|(?:\*\s*){3,})\s*$)|(?<!\*)\*[^\n*]+\*(?!\*)'),
    ('Markdown链接或图片', r'!?\[[^\n\]]*\]\([^\n)]*\)|(?m:^\s*\[[^\]\n]+\]:\s*\S+)'),
    ('Markdown列表或引用', r'(?m:^\s*(?:[-*+]\s+|>\s*|\d+[.)]\s+)[^\n]+)'),
    ('Markdown表格', r'(?m:^\s*\|.*\|\s*$)'),
    ('方括号或方头括号', r'\[[^\[\]\n]{0,200}\]|【[^【】\n]{0,200}】'),
    ('模板变量或花括号', r'\$?\{\{?[^{}\n]{0,200}\}\}?'),
    ('JSON字段包装', r'(?m:^[ \t]*\{?[ \t]*"(?:question|prompt|task_name|rubric|answer_approach|reference_answer)"\s*:)'),
    ('生成占位', r'TODO|TBD|请在此.{0,30}(?:填写|补充|生成)|待生成|占位符|placeholder'),
    ('模型或生产说明', r'作为(?:一个|一名)?\s*(?:AI|人工智能|语言模型)|根据\s*Skill|为了提高模型难度|以下是我生成|内部自检|系统提示词|本题设计了以下考点'),
    ('运行残留', r'tool_call(?:_id)?|Traceback \(most recent call last\)|/Users/[^\s<>"，。；]+|[A-Za-z]:\\Users\\[^\s<>"，。；]+|\b[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\b'),
    ('引用残留', r'[^\n]*|\bturn\d+(?:search|view|fetch)\d+\b|\[\^\d+\]'),
    ('转义或编码', r'\\(?:[nrt]|u[0-9a-fA-F]{4})|&(?:lt|gt|amp|quot|nbsp|#\d+|#x[0-9a-fA-F]+);'),
    ('回复包装', r'好的[，,].{0,15}(?:下面|开始)|希望对你有帮助|还需要我继续吗|以下是(?:为你|为您)?(?:整理|生成|设计)的题目'),
]


class ScanError(ValueError):
    pass


def mapping(value):
    if not isinstance(value, dict):
        raise ScanError('invalid_object')
    return value


def records(value):
    if not isinstance(value, list) or any(not isinstance(v, dict) for v in value):
        raise ScanError('invalid_list')
    return value


def required_text(value):
    if not isinstance(value, str) or not value.strip():
        raise ScanError('missing_text')
    return value


def narrow(item):
    item = mapping(item)
    return {key: required_text(item.get(key)) for key in ('workflow_id', 'title', 'question_version', 'question')}


def failure(error, workflow_id=None, stage='read'):
    code = str(error) if isinstance(error, ScanError) else ('http_error' if isinstance(error, HTTPError) else 'network_error' if isinstance(error, (URLError, OSError)) else 'invalid_response')
    return dict(workflow_id=workflow_id, stage=stage, code=code,
                **({'http_status': error.code} if isinstance(error, HTTPError) else {}))


def write_json(path, value):
    temp = path.with_name('.' + path.name + '.' + uuid.uuid4().hex)
    try:
        with temp.open('x', encoding='utf-8') as handle:
            os.chmod(temp, 0o600)
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write('\n')
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def scan(text):
    hits = []
    for category, pattern in PATTERNS:
        for match in re.finditer(pattern, text):
            start, end = match.span()
            hits.append(dict(category=category, start=start, end=end,
                             line=text.count('\n', 0, start) + 1,
                             column=start - text.rfind('\n', 0, start),
                             text=match.group(), context=text[max(0, start-60):min(len(text), end+60)],
                             verdict='candidate'))
    return sorted(hits, key=lambda h: (h['start'], h['end'], h['category']))


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('API重定向未接受，请核实本机地址')


def get(base, path):
    req = Request(base + path, method='GET', headers={'Accept': 'application/json'})
    with build_opener(NoRedirect).open(req, timeout=45) as response:
        return json.load(response)


def project_items(args, checkpoint):
    base = args.base_url.rstrip('/')
    url = urlsplit(base)
    if url.scheme != 'http' or url.hostname not in ('localhost', '127.0.0.1', '::1') or url.username or url.password or url.path or url.query or url.fragment:
        raise ValueError('base-url须为不含凭证及路径的本机HTTP地址')
    projects = get(base, '/api/projects')
    projects = records(projects)
    matches = [p for p in projects if p.get('id') == args.project_id] if args.project_id else [p for p in projects if p.get('name') == args.project]
    if len(matches) != 1:
        raise ValueError('项目名称/ID未唯一匹配，请核实或指定project-id')
    project = matches[0]
    required_text(project.get('id'))
    required_text(project.get('name'))
    route = '/api/projects/' + quote(project['id'], safe='')
    listing = mapping(get(base, route))
    workflows = records(listing.get('workflows'))
    if len({required_text(w.get('id')) for w in workflows}) != len(workflows):
        raise ValueError('工作流列表缺失/重复，不能证明完整覆盖')
    selected = [w for w in workflows if w.get('workflow_kind') == 'question' and
                (args.status == 'all' or w.get('current_decision') == args.status)]
    items, errors = [], []
    scope = dict(project_id=project['id'], project_name=project['name'], status=args.status,
                 listed_workflows=len(workflows), selected=len(selected), api=base)
    checkpoint(scope, items, errors)
    for w in selected:
        try:
            detail = mapping(get(base, '/api/workflows/' + quote(w['id'], safe='')))
            identity = mapping(detail.get('workflow'))
            if identity.get('project_id') != project['id'] or identity.get('id') != w['id']:
                raise ScanError('workflow_identity_mismatch')
            step_rows = records(detail.get('steps'))
            if any(type(s.get('ordinal')) is not int for s in step_rows) or len({s['ordinal'] for s in step_rows}) != len(step_rows):
                raise ScanError('invalid_steps')
            steps = {s['ordinal']: s for s in step_rows}
            author = steps[4]
            decision = steps.get(7, {})
            if args.status != 'all' and (decision.get('status') != 'succeeded' or mapping(decision.get('result') or {}).get('decision') != args.status):
                raise ScanError('decision_changed')
            result = mapping(author.get('result'))
            if author.get('status') != 'succeeded' or not isinstance(result.get('question'), str) or not result['question'].strip():
                raise ScanError('missing_current_prompt')
            if not result.get('question_version') or result['question_version'] != w.get('current_question_version'):
                raise ScanError('version_changed')
            # 其他正文不进入产物或Agent上下文。
            items.append(narrow(dict(workflow_id=w['id'], title=w.get('title'), question_version=result['question_version'], question=result['question'])))
        except (KeyError, TypeError, ValueError, HTTPError, URLError, OSError) as error:
            errors.append(failure(error, w['id']))
        checkpoint(scope, items, errors)
    def fingerprint(values):
        return sorted((w['id'], w.get('current_decision'), w.get('current_question_version')) for w in values if w.get('workflow_kind') == 'question')
    try:
        final = records(mapping(get(base, route)).get('workflows'))
        if fingerprint(workflows) != fingerprint(final):
            raise ScanError('scope_changed')
    except (KeyError, TypeError, ValueError, HTTPError, URLError, OSError) as error:
        errors.append(failure(error, stage='final_check'))
    checkpoint(scope, items, errors)
    return scope, items, errors


def offline(path):
    data = mapping(json.loads(path.read_text()))
    items = records(data.get('items'))
    clean = [narrow(item) for item in items]
    if len({i['workflow_id'] for i in clean}) != len(clean):
        raise ValueError('离线题目ID重复')
    errors = [] if data.get('complete') is True else [dict(stage='coverage', code='offline_scope_unverified')]
    return dict(source='offline', selected=len(clean), input=str(path)), clean, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--project')
    source.add_argument('--project-id')
    source.add_argument('--input', type=Path)
    parser.add_argument('--status', choices=['accepted', 'repair', 'all'], default='accepted')
    parser.add_argument('--base-url', default='http://127.0.0.1:3700')
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError('输出目录已存在，请使用新目录')
    args.out.mkdir(parents=True, mode=0o700)
    def checkpoint(scope, items, errors):
        write_json(args.out / 'progress.json', dict(scope=scope, complete=False, read=len(items), items=items, errors=errors))
    try:
        scope, items, errors = offline(args.input) if args.input else project_items(args, checkpoint)
    except (KeyError, TypeError, ValueError, OSError) as error:
        write_json(args.out / 'failure.json', failure(error, stage='collection'))
        raise
    for item in items:
        item['prompt_sha256'] = hashlib.sha256(item['question'].encode()).hexdigest()
    results = [dict(**{k: v for k, v in item.items() if k != 'question'}, matches=scan(item['question'])) for item in items]
    report = dict(scope=scope, observed_at=datetime.now(timezone.utc).isoformat(), complete=not errors,
                  collection_complete=not errors, scan_complete=True,
                  read=len(items), with_candidates=sum(bool(r['matches']) for r in results),
                  candidate_count=sum(len(r['matches']) for r in results), errors=errors, items=results)
    def write(name, text):
        path = args.out / name
        with path.open('x', encoding='utf-8') as handle:
            os.chmod(path, 0o600)
            handle.write(text)
    write('prompts.json', json.dumps(dict(scope=scope, complete=not errors, items=items), ensure_ascii=False, indent=2) + '\n')
    write('scan.json', json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    lines = ['# 题面扫描候选（未经语义确认）', '',
             f"范围：{json.dumps(scope, ensure_ascii=False)}", '',
             f"选中{scope['selected']}题，读取{len(items)}题，有候选{report['with_candidates']}题，候选{report['candidate_count']}处，失败/变化记录{len(errors)}条。", '',
             '仅扫描question。括号、Markdown、业务占位及引用内容须按用途判断；无命中不等于无任何残留。', '']
    for result in results:
        lines.extend([f"## {result['title']} · {result['workflow_id']}", f"版本：{result['question_version']}；候选：{len(result['matches'])}", ''])
        for hit in result['matches']:
            # 作为文本展示，避免命中的HTML/Markdown被报告界面执行或重新解释。
            excerpt = hit['context'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            lines.extend([f"- {hit['category']}；第{hit['line']}行第{hit['column']}列；字符[{hit['start']},{hit['end']})", '', '    ' + excerpt.replace('\n', '\n    '), ''])
    if errors:
        lines.extend(['## 未完成项', '', json.dumps(errors, ensure_ascii=False, indent=2)])
    write('候选清单.md', '\n'.join(lines))
    write_json(args.out / 'progress.json', dict(scope=scope, complete=not errors, read=len(items), errors=errors, artifacts=['prompts.json', 'scan.json', '候选清单.md']))
    print(json.dumps({k: v for k, v in report.items() if k != 'items'}, ensure_ascii=False))
    return 0 if report['complete'] else 2


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, KeyError, TypeError, OSError, HTTPError, URLError) as error:
        # 不输出原始API响应或可能含正文的异常对象。
        print('扫描未完成：请核实参数、服务与输入契约；未声明扫描通过。错误类型：' + type(error).__name__, file=sys.stderr)
        sys.exit(2)
