#!/usr/bin/env python3
"""将已确认的精确替换应用到题面本地副本；Skill调用，无API/数据库写入，原快照不变。"""
import argparse
import difflib
import hashlib
import json
import os
import sys
from pathlib import Path
from scan import mapping, records, required_text, narrow, write_json


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def build(snapshot, patch):
    originals = [narrow(x) for x in records(mapping(snapshot).get('items'))]
    by_id = {x['workflow_id']: x for x in originals}
    if len(by_id) != len(originals):
        raise ValueError('duplicate_source_id')
    changes, seen = [], set()
    for item in records(mapping(patch).get('items')):
        identity = required_text(item.get('workflow_id'))
        if identity in seen or identity not in by_id:
            raise ValueError('unknown_or_duplicate_patch_id')
        seen.add(identity)
        original = by_id[identity]
        before = original['question']
        if item.get('question_version') != original['question_version'] or item.get('prompt_sha256') != digest(before):
            raise ValueError('source_version_or_hash_mismatch')
        edits = records(item.get('edits'))
        if not edits:
            raise ValueError('empty_edits')
        ordered = sorted(edits, key=lambda e: e.get('start') if type(e.get('start')) is int else -1)
        last = 0
        for edit in ordered:
            start, end = edit.get('start'), edit.get('end')
            if type(start) is not int or type(end) is not int or not last <= start < end <= len(before):
                raise ValueError('invalid_or_overlapping_range')
            if edit.get('confirmed') is not True or not isinstance(edit.get('after'), str):
                raise ValueError('unconfirmed_or_invalid_edit')
            required_text(edit.get('reason'))
            if before[start:end] != edit.get('before'):
                raise ValueError('original_text_mismatch')
            last = end
        after = before
        for edit in reversed(ordered):
            after = after[:edit['start']] + edit['after'] + after[edit['end']:]
        if not after.strip() or after == before:
            raise ValueError('empty_or_unchanged_prompt')
        changes.append(dict(workflow_id=identity, title=original['title'],
                            source_question_version=original['question_version'],
                            source_prompt_sha256=digest(before), new_prompt_sha256=digest(after),
                            original_question=before, proposed_question=after, edits=ordered,
                            state='local_draft_not_saved_to_api'))
    return changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--patch', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError('output_exists')
    changes = build(json.loads(args.input.read_text()), json.loads(args.patch.read_text()))
    args.out.mkdir(parents=True, mode=0o700)
    write_json(args.out / 'changes.json', dict(state='local_drafts_only', items=changes))
    path = args.out / 'changes.diff'
    with path.open('x', encoding='utf-8') as handle:
        os.chmod(path, 0o600)
        for change in changes:
            identity = change['workflow_id']
            handle.writelines(difflib.unified_diff([line + '\n' for line in change['original_question'].splitlines()],
                                                  [line + '\n' for line in change['proposed_question'].splitlines()],
                                                  fromfile=identity + '/original', tofile=identity + '/proposed'))
            handle.write('\n')
    print(json.dumps(dict(changed=len(changes), state='local_drafts_only'), ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print('未生成修改：输入/补丁校验或文件操作失败；错误类型：' + type(error).__name__, file=sys.stderr)
        sys.exit(2)
