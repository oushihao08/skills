---
name: verification-before-completion
description: Use when about claim work complete, fixed, or passing, before committing or creating PRs - requires running verification commands and confirming output before making any success claims; evidence before assertions always
---

# Verification Before Completion

## Overview

Claiming work complete without verification is dishonesty, not efficiency.

**Core principle:** Evidence before claims. Always.

## The Iron Law

NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE

If you have not run verification command in current work, you cannot claim it passes.

## The Gate Function

1. Identify what command proves claim.
2. Run full command, fresh and complete.
3. Read full output, exit code, failure count.
4. Verify output confirms claim.
5. Only then make claim.

Skip step = false claim.

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test output with 0 failures | Previous run, guess |
| Linter clean | Linter output with 0 errors | Partial check |
| Build succeeds | Build exit 0 | Linter passing |
| Bug fixed | Reproduce original symptom and pass | Code changed |
| Requirements met | Checklist against requirement | Tests passing |
| Agent completed | Diff and verification | Agent says success |

## Red Flags

- "should"
- "probably"
- "seems to"
- satisfaction before verification
- commit/push/PR before verification
- trusting agent success report
- partial verification

## Bottom Line

Run command. Read output. Then claim result.
