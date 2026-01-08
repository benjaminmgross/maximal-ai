---
description: Deep analysis of specific technical decisions with tradeoff evaluation and recommendations
---

# Tradeoff Analysis

You are tasked with conducting a focused tradeoff analysis for a specific technical decision. This command provides deep research and structured evaluation to help make informed architectural choices.

<decision_question>
$ARGUMENTS
</decision_question>

## Initial Setup

When this command is invoked:

1. **If a decision question was provided**:
   - Acknowledge the question
   - Proceed to analyze the tradeoff

2. **If no question provided**, respond with:
```
I'm ready to analyze a technical tradeoff. Please describe:
- The decision you need to make (e.g., "SQL vs NoSQL for user data")
- Any relevant context or constraints
- What factors matter most to you
```

Then wait for the user's response.

## Process Steps

### Step 1: Load Decision Framework

Read the tradeoff decision trees:

```
Read: .claude/docs/system-design/tradeoff-decision-trees.md
```

This provides structured frameworks for common decisions.

### Step 2: Clarify Decision Context

Use AskUserQuestion to gather critical context. Ask ONE question at a time:

**Core Context:**
```
What type of decision is this?
(A) Database selection (SQL vs NoSQL, specific DB choice)
(B) Architecture style (monolith vs microservices, sync vs async)
(C) Communication protocol (REST vs GraphQL vs gRPC)
(D) Infrastructure (cloud vs on-prem, serverless vs containers)
(E) Other - please describe
```

**Scale Context:**
```
What scale are you designing for?
(A) Small - hundreds of users, GBs of data
(B) Medium - thousands of users, TBs of data
(C) Large - millions of users, PBs of data
(D) Unknown - need to figure this out
```

**Constraints:**
```
What constraints exist? (select all that apply)
(A) Must use existing tech stack
(B) Team lacks expertise in Option X
(C) Budget constraints
(D) Timeline pressure
(E) Compliance/regulatory requirements
(F) None significant
```

**Priority:**
```
What's most important for this decision?
(A) Performance - speed is critical
(B) Scalability - growth is expected
(C) Simplicity - team productivity matters most
(D) Cost - budget is constrained
(E) Flexibility - requirements may change
```

**Skip questions if** the user provided sufficient context upfront.

### Step 3: Apply Decision Framework

Check if the decision type is covered in `tradeoff-decision-trees.md`.

**If covered:**
Walk through the decision tree with the user's context:
```
Applying the [Decision Type] decision framework:

1. [Decision point 1]?
   Your context: [Answer based on gathered info]
   → Points to: [Option]

2. [Decision point 2]?
   Your context: [Answer based on gathered info]
   → Points to: [Option]

Framework suggests: [Option]
```

**If not covered:**
Build a custom decision matrix for the specific options.

### Step 4: Research Options

Spawn the `tradeoff-researcher` agent for deep analysis:

```
Research the tradeoff between [Option A] and [Option B] for [specific context].

Context:
- Scale: [from user]
- Constraints: [from user]
- Priority: [from user]
- Use case: [specific use case]

Research:
1. Best practices for this decision in similar contexts
2. Performance benchmarks if available
3. Case studies from comparable companies
4. Long-term maintenance implications
5. Migration paths if decision needs to change

Return structured analysis with sources.
```

### Step 5: Synthesize Analysis

Combine framework analysis with research findings.

Present to user:
```
## Analysis Summary

**Framework Recommendation:** [Option from decision tree]
**Research Recommendation:** [Option from agent research]
**Alignment:** [Agree/Disagree - explanation if disagree]

**Key Factors:**
| Factor | Option A | Option B | Your Priority |
|--------|----------|----------|---------------|
| [Factor] | [Rating] | [Rating] | [High/Med/Low] |

**Weighted Recommendation:** [Final option]
```

### Step 6: Generate Tradeoff Document

Detect username for file naming:
```bash
if [ -f ".claude/config.yaml" ]; then
    CONFIG_USERNAME=$(grep "^username:" .claude/config.yaml | cut -d: -f2 | tr -d ' ' | tr '[:upper:]' '[:lower:]')
fi
RPI_USERNAME="${CONFIG_USERNAME:-${RPI_USERNAME:-$(git config user.name | tr ' ' '-' | tr '[:upper:]' '[:lower:]')}}"
RPI_USERNAME="${RPI_USERNAME:-user}"
CURRENT_DATE=$(date +%Y.%m.%d)
```

Create document at `thoughts/research/YYYY.MM.DD-{username}-{decision}-tradeoff.md`:

```markdown
---
date: [ISO datetime]
analyst: [name]
decision: [brief decision description]
recommendation: [recommended option]
confidence: high/medium/low
type: tradeoff-analysis
status: complete
---

# Tradeoff Analysis: [Decision Title]

**Date:** [ISO datetime]
**Analyst:** [name]
**Decision:** [What needs to be decided]
**Recommendation:** [Option] with [confidence] confidence

## Executive Summary

[2-3 sentences on the decision, recommendation, and key reasoning]

## Decision Context

### Problem Statement
[What problem are we solving? Why does this decision matter?]

### Constraints
- **Scale:** [Scale context]
- **Timeline:** [Timeline pressure]
- **Budget:** [Budget constraints]
- **Team:** [Team expertise]
- **Compliance:** [Any regulatory requirements]

### Priority Order
1. [Most important factor]
2. [Second most important]
3. [Third most important]

## Options Analyzed

### Option A: [Name]

**Description:**
[What this option entails]

**Pros:**
- ✅ [Pro 1 with evidence]
- ✅ [Pro 2 with evidence]
- ✅ [Pro 3 with evidence]

**Cons:**
- ❌ [Con 1 with evidence]
- ❌ [Con 2 with evidence]

**Best When:**
- [Scenario 1]
- [Scenario 2]

**Avoid When:**
- [Scenario 1]
- [Scenario 2]

**Real-World Examples:**
- [Company/project using this approach]

### Option B: [Name]

[Same structure as Option A]

### Option C: [Name] (if applicable)

[Same structure]

## Comparison Matrix

| Factor | Weight | Option A | Option B | Option C |
|--------|--------|----------|----------|----------|
| Performance | [1-5] | ⭐⭐⭐⭐☆ | ⭐⭐⭐☆☆ | ⭐⭐⭐⭐⭐ |
| Scalability | [1-5] | ⭐⭐⭐☆☆ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐☆ |
| Simplicity | [1-5] | ⭐⭐⭐⭐⭐ | ⭐⭐☆☆☆ | ⭐⭐⭐☆☆ |
| Cost | [1-5] | ⭐⭐⭐⭐☆ | ⭐⭐⭐☆☆ | ⭐⭐☆☆☆ |
| Team fit | [1-5] | ⭐⭐⭐⭐⭐ | ⭐⭐⭐☆☆ | ⭐⭐☆☆☆ |
| **Weighted Score** | | **X/25** | **Y/25** | **Z/25** |

## Decision Framework Application

From `.claude/docs/system-design/tradeoff-decision-trees.md`:

```
Decision Tree: [Type]

1. [Question 1]?
   → Your answer: [Answer]
   → Suggests: [Option]

2. [Question 2]?
   → Your answer: [Answer]
   → Suggests: [Option]

3. [Question 3]?
   → Your answer: [Answer]
   → Suggests: [Option]

Framework conclusion: [Option]
```

## Research Findings

### Industry Best Practices
[Findings from research with sources]

### Performance Data
[Any benchmarks or performance comparisons]

### Case Studies

#### [Company/Project 1]
- **Context:** [Similar to ours because...]
- **Choice:** [What they chose]
- **Outcome:** [How it worked out]
- **Source:** [Link]

#### [Company/Project 2]
[Same structure]

### Community Consensus
[What the developer community generally recommends]

## Recommendation

### Primary Recommendation: [Option]

**Confidence Level:** High/Medium/Low

**Rationale:**
1. [Primary reason with evidence]
2. [Secondary reason with evidence]
3. [Tertiary reason with evidence]

**Key Assumptions:**
- [Assumption 1 that affects this recommendation]
- [Assumption 2]

### Alternative Recommendation

If [condition], consider [Option B] instead because [reason].

## Risk Analysis

### Risks of Recommended Option

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | Low/Med/High | Low/Med/High | [How to mitigate] |
| [Risk 2] | Low/Med/High | Low/Med/High | [How to mitigate] |

### Risks of NOT Choosing This Option

| Risk | Likelihood | Impact |
|------|------------|--------|
| [Risk 1] | Low/Med/High | Low/Med/High |

## Reversibility Analysis

**How hard is it to change this decision later?**

### Migration Path: [Recommended] → [Alternative]
- **Effort:** Low/Medium/High
- **Timeline:** [Estimate]
- **Steps:**
  1. [Step 1]
  2. [Step 2]

### Lock-in Concerns
- [Any vendor/technology lock-in to be aware of]

## Implementation Implications

### If We Choose [Recommended Option]:
- **Setup effort:** [Estimate]
- **Learning curve:** [Low/Medium/High]
- **Team training needed:** [Yes/No - details]
- **Infrastructure changes:** [What needs to change]

### Key Success Factors:
1. [What needs to go right]
2. [What to watch out for]

## When to Revisit This Decision

Reconsider if:
- [ ] Scale exceeds [threshold]
- [ ] Requirements change to include [feature]
- [ ] [Constraint] is removed
- [ ] Performance degrades below [threshold]

## Summary

| Aspect | Value |
|--------|-------|
| Recommended | [Option] |
| Confidence | [Level] |
| Key driver | [Most important factor] |
| Reversibility | [Easy/Medium/Hard] |
| Review trigger | [When to reconsider] |

## Research Sources

- [Source 1 - Title](URL)
- [Source 2 - Title](URL)
- [Source 3 - Title](URL)
```

### Step 7: Present and Confirm

Summarize for the user:
```
## Tradeoff Analysis Complete

**Decision:** [Question]
**Recommendation:** [Option] with [confidence] confidence

**Top 3 Reasons:**
1. [Reason 1]
2. [Reason 2]
3. [Reason 3]

**Full analysis:** thoughts/research/YYYY.MM.DD-{username}-{decision}-tradeoff.md

Would you like to:
(A) Discuss any aspect in more detail
(B) Explore an alternative recommendation
(C) Proceed with implementation
(D) Share this analysis with the team
```

## Common Tradeoff Types

This command handles:
- **Database:** SQL vs NoSQL, PostgreSQL vs MySQL, etc.
- **Architecture:** Monolith vs Microservices, CQRS vs CRUD
- **Communication:** REST vs GraphQL vs gRPC, Sync vs Async
- **Infrastructure:** Serverless vs Containers, Cloud vs On-prem
- **Caching:** Redis vs Memcached, strategy selection
- **Consistency:** Strong vs Eventual, CAP tradeoffs

## Important Notes

- **Be objective**: Present honest pros/cons for all options
- **Cite sources**: Back claims with evidence
- **Consider context**: No universally "best" answer
- **Acknowledge uncertainty**: State confidence levels
- **Plan for change**: Include reversibility analysis

## Success Indicators

Good tradeoff analyses:
- Have clear recommendation with reasoning
- Present balanced view of all options
- Include real-world evidence
- Consider long-term implications
- Provide actionable decision criteria
