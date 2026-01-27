# Extension Guide: Adapting the Three-Phase Workflow to Any Domain

## Core Framework

The system is domain-agnostic. It works for any complex task that benefits from:
1. Understanding before doing
2. Planning before executing
3. Verification during execution

## Step-by-Step Adaptation Guide

### Step 1: Map Your Domain's Phases

Ask yourself:
- **Research Phase**: What do I need to understand?
- **Planning Phase**: What do I need to design?
- **Implementation Phase**: What do I need to execute?

### Step 2: Create Your Command Structure

Create three new commands in `.claude/commands/`:

#### `[domain]_research.md`
```markdown
# [Domain] Research

You are tasked with researching [domain-specific context].

## Initial Setup
[Greeting and explanation]

## Research Process
1. [Domain-specific research step 1]
2. [Domain-specific research step 2]
3. [Synthesis step]

## Output Format
[Domain-specific research document structure]
```

#### `[domain]_plan.md`
```markdown
# [Domain] Plan

You are tasked with planning [domain-specific objective].

## Planning Process
1. Read research document
2. [Domain-specific planning steps]
3. Create actionable plan

## Output Format
[Domain-specific plan structure]
```

#### `[domain]_implement.md`
```markdown
# [Domain] Implementation

You are tasked with executing [domain-specific plan].

## Implementation Process
1. Read plan document
2. [Domain-specific execution steps]
3. Verify success

## Success Criteria
[Domain-specific verification]
```

### Step 3: Design Domain-Specific Agents

Create specialized agents in `.claude/agents/`:

```markdown
---
name: [domain]-[specialist]
description: [What this agent specializes in]
tools: [Relevant tools]
model: sonnet
---

You are a specialist at [specific domain task].

## Core Responsibilities
1. [Responsibility 1]
2. [Responsibility 2]

## Search Strategy
[How to find information]

## Output Format
[How to structure findings]
```

**Model Selection:** Use `model: sonnet` (recommended default) for most agents. The model field is optional but recommended. Available options: `sonnet` (balanced speed/capability), `opus` (maximum capability), `haiku` (fastest, for simple tasks).

### Step 4: Define Document Templates

Create templates for each phase's output.

## Concrete Examples

### Example 1: Product Management

#### Phases
1. **Market Research** → Understand users, market, competition
2. **Product Planning** → Design features, specifications, roadmap
3. **Launch Execution** → Implement go-to-market strategy

#### Commands
- `/market_research [product area]`
- `/product_plan research/[date]-[area].md`
- `/launch_execute plans/[date]-[product].md`

#### Agents
- `user-researcher` - Analyzes user needs and feedback
- `market-analyzer` - Studies market trends
- `competitor-analyst` - Tracks competitive landscape
- `stakeholder-mapper` - Identifies key stakeholders

#### Document Flow
```
market-research/
├── 2025-01-12-mobile-payments.md
product-plans/
├── 2025-01-12-tap-to-pay.md
launch-plans/
├── 2025-01-12-tap-to-pay-gtm.md
```

### Example 2: Data Science

#### Phases
1. **Data Exploration** → Understand data, patterns, quality
2. **Model Design** → Plan architecture, features, metrics
3. **Model Training** → Implement and validate model

#### Commands
- `/explore_data [dataset/problem]`
- `/design_model exploration/[date]-[dataset].md`
- `/train_model designs/[date]-[model].md`

#### Agents
- `data-profiler` - Analyzes data quality and distributions
- `feature-engineer` - Identifies valuable features
- `model-researcher` - Finds relevant papers and approaches
- `metric-designer` - Defines evaluation criteria

#### Document Flow
```
explorations/
├── 2025-01-12-customer-churn.md
model-designs/
├── 2025-01-12-churn-prediction.md
training-runs/
├── 2025-01-12-churn-model-v1.md
```

### Example 3: Content Creation

#### Phases
1. **Content Research** → Topic research, audience analysis
2. **Content Planning** → Outline, structure, key points
3. **Content Production** → Writing, editing, publishing

#### Commands
- `/content_research [topic/keyword]`
- `/content_plan research/[date]-[topic].md`
- `/content_write plans/[date]-[title].md`

#### Agents
- `topic-researcher` - Deep dives into subject matter
- `audience-analyzer` - Understands target readers
- `seo-optimizer` - Researches keywords and competition
- `fact-checker` - Verifies claims and sources

#### Document Flow
```
topic-research/
├── 2025-01-12-ai-context-engineering.md
content-plans/
├── 2025-01-12-context-engineering-guide.md
published/
├── 2025-01-12-ultimate-context-guide.md
```

## Implementation Checklist

When creating a new domain extension:

### Phase 1: Discovery
- [ ] Identify the three phases for your domain
- [ ] List key questions each phase must answer
- [ ] Define success criteria for each phase
- [ ] Identify required tools and data sources

### Phase 2: Design
- [ ] Create command files for each phase
- [ ] Design specialized agents (3-5 typically)
- [ ] Define document templates
- [ ] Plan directory structure

### Phase 3: Implementation
- [ ] Copy base system to new location
- [ ] Modify commands for your domain
- [ ] Create domain-specific agents
- [ ] Test with a simple example
- [ ] Refine based on results

## Key Principles to Maintain

Regardless of domain, always maintain:

1. **Context Resets Between Phases**
   - Each phase starts fresh
   - Only carries forward the MD document

2. **Parallel Agent Architecture**
   - Research uses multiple specialized agents
   - Agents work in parallel, not sequence
   - Main context synthesizes, doesn't explore

3. **Reviewable Artifacts**
   - Each phase outputs a reviewable document
   - Documents are self-contained
   - Human review before next phase

4. **Progressive Refinement**
   - Research reduces uncertainty
   - Planning reduces ambiguity
   - Implementation reduces risk

5. **Clear Success Criteria**
   - Automated where possible
   - Manual where necessary
   - Measurable always

## Anti-Patterns to Avoid

### Don't:
- Skip phases to save time
- Combine phases in one context
- Proceed with open questions
- Ignore domain conventions
- Create overly complex agents

### Do:
- Complete each phase fully
- Reset context between phases
- Resolve all ambiguities
- Follow domain best practices
- Keep agents focused and simple

## Testing Your Extension

1. **Start Small**: Test with a simple, well-understood task
2. **Validate Outputs**: Check each phase's document quality
3. **Measure Efficiency**: Track context usage (<40% target)
4. **Iterate Quickly**: Refine based on what you learn
5. **Document Patterns**: Capture what works for your domain

## Success Indicators

Your domain extension is working when:
- Research documents answer all key questions
- Plans are approved without major revisions
- Implementation proceeds without blocking
- Context stays under 40% in each phase
- Output quality matches or exceeds manual work
- Time to completion is significantly reduced

## Final Note

The power isn't in the specific commands or agents - it's in the pattern:

```
UNDERSTAND → DESIGN → EXECUTE
```

With intentional context management at each transition.

This pattern is universal. The specifics are just implementation details.

Start with the pattern. The rest will follow.