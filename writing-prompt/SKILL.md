---
name: writing-prompt
description: 'Use when writing prompts for AI - system prompts, agents, skills, or AI model instructions. Apply AI-first design: structured > verbose, examples only when necessary, token efficiency priority. Trigger on "create a prompt", "write agent", "design skill".'
---

# Writing Prompts

## Core Mission

Generate optimized prompts following principle: **AI consumption, not human documentation**. Convert intent into context-aware decision rules; do not convert one task's answer, example, topic, count, or preference into a permanent rule.

**Formula:** Clear instructions + Context hierarchy + Structured decision rules + Model-specific optimization = Effective Prompts

## Core Rule: Context Before Examples

Prompt rules have two classes. Keep them separate:

| Class | Source | Treatment |
|---|---|---|
| 固定系统边界 | safety, tool capability, platform scope, permitted side effects | State explicitly and apply consistently. |
| 动态任务条件 | topic, exclusions, quantity, date range, labels, ranking, output detail | Resolve from the current request, prompt context, reference documents, configuration, and tool results. Do not hard-code it. |

Resolve competing dynamic conditions in this order（条件优先级）：

```text
用户当前要求 > 当前任务提示词 > 适用的参考文档/配置 > 工具能力 > 模型默认判断
```

Do not let a lower-priority default override a clear current request. If a dynamic condition is missing, preserve uncertainty or ask the smallest blocking question; do not invent a restrictive preference. 相关性判断必须基于当前任务上下文，不得把示例、历史结果或模型偏好当成默认条件。

<context_contract>
  <rule id="classify">Classify each instruction as fixed boundary, dynamic condition, evidence, example, or output requirement.</rule>
  <rule id="resolve">Resolve dynamic conditions from the current context before planning or writing.</rule>
  <rule id="scope">Apply exclusions only when explicitly requested, defined by applicable references, or proven irrelevant to the task.</rule>
  <rule id="generalize">Treat examples as demonstrations, not defaults, unless the prompt explicitly marks them as defaults.</rule>
  <rule id="trace">For every non-obvious restriction, record its source and scope.</rule>
  <rule id="separate-counts">Separate discovery, candidate, accepted, analyzed, and delivered counts; never turn one run's counts into a permanent quota.</rule>
</context_contract>

### Required Abstracting Test

Before finalizing a prompt, replace every concrete topic, product, number, date, platform, or exclusion with a new value and re-evaluate the instruction. If the rule still incorrectly rejects or requires the original value, rewrite it as a context-dependent condition.

Bad:

> Do not search medical content. Return five posts.

Good:

> Search only content relevant to the current objective and explicit scope. Use the current task's requested delivery count; choose discovery volume from available data, budget, time range, and tool limits.

The example is not a permanent medical exclusion or a fixed five-item quota.

## AI-First Design Principles

<critical_principle>
Prompts are consumed by AI models, not humans. Design for machine parsing and execution.
</critical_principle>

<framework>
  <principle id="context_over_case">
    <description>Write the decision basis, not the answer from one past case. Keep current context and reference evidence available to the model.</description>
  </principle>
  <principle id="boundary_condition_separation">
    <description>Separate immutable safety/tool boundaries from user-controlled task conditions. Fixed boundaries may be strict; dynamic conditions must be resolved per task.</description>
  </principle>
  <principle id="source_and_scope">
    <description>Attach every non-obvious restriction to an authority and scope. Do not expand a local example into a global rule.</description>
  </principle>
  <principle id="structure_over_explanation">
    <description>Use structured formats over verbose text</description>
    <bad_example>Long narrative explanations</bad_example>
    <good_example>XML tags, JSON, concise lists</good_example>
  </principle>

  <principle id="token_efficiency">
    <description>Every token must add value</description>
    <checklist>
      <item>No examples for simple operations</item>
      <item>Single field < 50 words unless critical</item>
      <item>No redundant descriptions</item>
      <item>Remove all "obvious" explanations</item>
    </checklist>
    <target>< 2000 tokens for agent/skill definitions</target>
  </principle>

  <principle id="example_minimalism">
    <description>Include examples only when absolutely necessary</description>
    <include_when>
      <condition>Complex output format (nested JSON schema)</condition>
      <condition>Ambiguous decision criteria ("High" vs "Medium" priority)</condition>
      <condition>Boundary conditions (when to skip/abort)</condition>
      <condition>Subtle distinctions that confuse AI</condition>
    </include_when>
    <skip_when>
      <condition>Simple sequential instructions</condition>
      <condition>Common concepts ("past 2 weeks", "use Read tool")</condition>
      <condition>Obvious operations</condition>
      <condition>Tool usage (documentation exists)</condition>
    </skip_when>
    <decision_tree>
      <question>Is instruction complex or ambiguous?</question>
      <branch yes="Provide 1-2 examples" no="Skip examples" />
    </decision_tree>
  </principle>

  <principle id="imperative_language">
    <description>Use direct commands, not suggestions</description>
    <bad> "You should...", "We recommend...", "Consider..."</bad>
    <good> "Do X", "Use Y", "Always...", "Never..."</good>
  </principle>
</framework>

## Prompt Structure Templates

### System/Agent Prompt Template

```xml
<role>
You are [ROLE] with expertise in:
- [EXPERTISE_AREA_1]
- [EXPERTISE_AREA_2]
</role>

<core_mission>
[WHAT_THIS_AGENT_DOES]
</core_mission>

<responsibilities>
When [TASK_TYPE], always:
1. [PRINCIPLE_1]
2. [PRINCIPLE_2]
3. [PRINCIPLE_3]
</responsibilities>

<tool_usage>
- Read files before editing (never assume)
- Use Edit tool for changes (not bash sed/echo)
- Execute independent operations in parallel
- Delegate to subagents when beneficial
</tool_usage>

<context_management>
- Track token budget efficiently
- Save progress before context refresh
- Use structured formats (JSON) for state data
</context_management>

<output_style>
- Be concise and direct
- Avoid excessive markdown formatting
- Provide specific file paths and line numbers
</output_style>

<constraints>
- Do NOT over-engineer
- Do NOT add features beyond scope
- Do NOT refactor unless requested
- Validate at system boundaries only
</constraints>
```

### Skill Definition Template (SKILL.md)

```markdown
---
name: skill-name
description: Use when [specific trigger conditions]. Apply [core method].
---

# Skill Title

## Core Mission

[What this skill does in 1-2 sentences]

## Framework

<framework>
  <process>
    <step id="1" name="[STEP_NAME]">
      <method>[What to do]</method>
      <output>[Expected result]</output>
    </step>
  </process>
</framework>

## Integration Points

<triggers>
  <auto>[When to trigger automatically]</auto>
  <manual>[User phrases that trigger]</manual>
</triggers>

## Output Format

<output_structure>
  <section>[What to output]</section>
</output_structure>
```

## Claude 4.5 Optimizations

<optimizations>
  <context_awareness>
    Context window auto-compacts on limit
    → Do NOT stop tasks due to token budget
    → Save progress before context refresh
    → Be persistent and complete tasks fully
  </context_awareness>

  <parallel_execution>
    If multiple tool calls have no dependencies
    → Execute in parallel (maximize efficiency)
    → Never use placeholders or guess parameters
  </parallel_execution>

  <subagent_delegation>
    Delegate when:
    - Separate context window needed
    - Specialized capabilities required
    - Parallel execution beneficial
  </subagent_delegation>

  <hallucination_prevention>
    NEVER speculate about unopened code
    ALWAYS read files before answering
    Give grounded, evidence-based responses
  </hallucination_prevention>
</optimizations>

## Common Pitfalls

<anti_patterns>
  <pattern severity="critical">
    <name>Over-engineering</name>
    <sign>More than 3 examples for single concept</sign>
    <sign>Single field > 100 words</sign>
    <sign>Python pseudo-code for simple logic</sign>
    <fix>Use structured format, remove redundancy</fix>
  </pattern>

  <pattern severity="high">
    <name>Example bloat</name>
    <sign>Examples for simple operations</sign>
    <sign>Redundant examples</sign>
    <fix>Apply critical thinking: is this example necessary?</fix>
  </pattern>

  <pattern severity="medium">
    <name>Vague instructions</name>
    <sign>"Help me with code"</sign>
    <sign>Missing scope/format/constraints</sign>
    <fix>Specify exactly: what, scope, format, constraints</fix>
  </pattern>

  <pattern severity="critical">
    <name>Case-to-rule leakage</name>
    <sign>A concrete topic, number, date, label, or exclusion from one task appears as a universal instruction.</sign>
    <fix>Classify it as a dynamic condition, attach its source and scope, then resolve it from the current context.</fix>
  </pattern>
</anti_patterns>

## Prompt Generation Workflow

<workflow>
  <step id="1" name="gather_requirements">
    <questions>
      <q>What is the task? (specific goal)</q>
      <q>What type of prompt? (system/agent/skill/task)</q>
      <q>Who is audience? (target user/expertise)</q>
      <q>What is context? (background, motivation, constraints)</q>
    </questions>
  </step>

  <step id="1a" name="classify_rules">
    <actions>
      <action>Separate fixed system boundaries from dynamic task conditions.</action>
      <action>Mark examples, defaults, evidence, exclusions, and output requirements explicitly.</action>
      <action>Record the source and scope of every non-obvious restriction.</action>
    </actions>
  </step>

  <step id="1b" name="resolve_context">
    <actions>
      <action>Resolve dynamic conditions using current user intent, prompt context, applicable references/configuration, and tool capability in that order.</action>
      <action>Do not inherit a topic, count, date, label, or exclusion from an example or prior task unless the current context confirms it.</action>
      <action>Preserve uncertainty or ask one blocking question when a required condition is missing.</action>
    </actions>
  </step>

  <step id="2" name="design_structure">
    <actions>
      <action>Choose template (system/agent/skill)</action>
      <action>Define core mission (1-2 sentences)</action>
      <action>Identify key sections (role, process, constraints)</action>
      <action>Apply XML structure if complex</action>
    </actions>
  </step>

  <step id="3" name="optimize">
    <checks>
      <check>Remove all non-essential examples</check>
      <check>Convert verbose text to structured format</check>
      <check>Ensure single field < 50 words</check>
      <check>Use imperative language throughout</check>
      <check>Target < 2000 tokens (agent/skill)</check>
    </checks>
  </step>

  <step id="4" name="validate">
    <criteria>
      <criterion>Instructions explicit and unambiguous</criterion>
      <criterion>Context explains motivation</criterion>
      <criterion>Fixed boundaries and dynamic conditions are separated</criterion>
      <criterion>Current user intent overrides lower-priority defaults</criterion>
      <criterion>No example has silently become a global rule</criterion>
      <criterion>Restrictions have an identifiable source and scope</criterion>
      <criterion>Discovery, accepted, analyzed, and delivered counts are not conflated</criterion>
      <criterion>Examples only when necessary</criterion>
      <criterion>Model-specific optimizations applied</criterion>
      <criterion>Token-efficient</criterion>
    </criteria>
  </step>
</workflow>

## OpenAI-Specific Patterns

<message_roles>
  <developer>Highest priority: System rules, business logic</developer>
  <user>End user inputs, configuration</user>
  <assistant>Model's previous responses</assistant>
</message_roles>

<output_formatting>
  <structured_output>
    For JSON outputs, specify exact schema:
    Respond ONLY with valid JSON matching this structure:
    { "field": "type" }
    Do NOT include text outside JSON
  </structured_output>
</output_formatting>

## Verification Checklist

<checklist>
  <item>Instructions explicit and unambiguous</item>
  <item>Context explains motivation</item>
  <item>Classify every rule as fixed boundary, dynamic condition, evidence, example, or output requirement</item>
  <item>Resolve dynamic conditions from current context before applying defaults</item>
  <item>Do not convert examples, topics, counts, or past outputs into permanent rules</item>
  <item>Apply exclusions only when sourced and scoped</item>
  <item>Separate discovery, candidate, accepted, analyzed, and delivered counts</item>
  <item>Run the concrete-value substitution test on non-obvious rules</item>
  <item>Examples only when complex/ambiguous (not simple/obvious)</item>
  <item>Tools explicitly mentioned (if agent)</item>
  <item>Constraints prevent unwanted behavior</item>
  <item>Role well-defined (if applicable)</item>
  <item>Model-specific optimizations applied</item>
  <item>Token-efficient (< 2000 tokens for agents)</item>
  <item>Imperative language used throughout</item>
  <item>Structured format (XML) for complex prompts</item>
</checklist>

## Quick Reference

| Technique | When to Use | Pattern |
|-----------|-------------|---------|
| Role definition | System/agent prompts | "You are [ROLE] with expertise in..." |
| XML tags | Complex structure | `<task>...</task><scope>...</scope>` |
| Examples | ONLY when complex/ambiguous | Input: "X" → Output: "Y" (1-2 max) |
| Context | All non-trivial prompts | "This is for [PROJECT] because..." |
| Constraints | Prevent unwanted behavior | "Do NOT use [X]" |
| Parallel execution | Independent operations | "Execute in parallel: [list]" |
| Structured output | JSON/formatted data | "Respond ONLY with: [schema]" |

**Key**: Examples are rare exceptions, not default. Critical thinking required.

---

Last updated: January 2025 (Version 3.0.0)
Models: Claude Sonnet 4.5, Opus 4.5, Haiku 4.5, GPT-5

**Version 3.0.0 Changes:**
- ✅ Reduced from 904 to ~240 lines (74% reduction)
- ✅ Removed all non-essential examples
- ✅ Structured format with XML tags
- ✅ Token efficiency priority throughout
- ✅ Imperative language enforcement
- ✅ Clear anti-patterns section
- ✅ Simplified workflow

**Why This Matters:**
Prompts are **machine instructions**, not human tutorials. Over-engineering wastes tokens, reduces flexibility, violates AI-first principles.

**Impact:**
Expected 60-80% token reduction while maintaining or improving AI comprehension.
