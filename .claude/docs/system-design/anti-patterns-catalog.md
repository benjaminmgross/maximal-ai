# Anti-Patterns Catalog

Reference guide for identifying and avoiding common architectural anti-patterns. Use this during code reviews and architecture assessments.

---

## God Object / God Class

### Description
A class or module that knows too much or does too much. Violates single responsibility principle, becomes maintenance nightmare.

### Detection Heuristics

**Code smells:**
- Class with > 500-1000 lines
- Too many public methods (> 15-20)
- Too many dependencies injected
- Name includes "Manager", "Handler", "Helper", "Util" with broad scope
- Every feature touches this class

**Grep patterns:**
```bash
# Find large files (potential God Objects)
find . -name "*.py" -exec wc -l {} \; | sort -rn | head -20
find . -name "*.ts" -exec wc -l {} \; | sort -rn | head -20

# Find classes with many methods
grep -r "def " filename.py | wc -l  # Python
grep -r "function\|async\|=>" filename.ts | wc -l  # TypeScript
```

**Structural signals:**
- File modified in nearly every PR
- High merge conflict frequency
- Long import lists
- Multiple unrelated responsibilities

### Impact
- **Maintainability**: Changes have ripple effects
- **Testability**: Hard to test in isolation
- **Team**: Bottleneck for parallel work
- **Understanding**: Hard to comprehend full scope

### Resolution
1. **Identify responsibilities** - List distinct things the class does
2. **Extract cohesive groups** - Move related methods to new classes
3. **Apply SRP** - One reason to change per class
4. **Use composition** - Small focused classes composed together

---

## Distributed Monolith

### Description
Services are deployed separately but tightly coupled—all the complexity of microservices with none of the benefits. Must deploy together, share databases, synchronous call chains.

### Detection Heuristics

**Deployment signals:**
- Services must deploy together or break
- Shared database across services
- Deploy scripts mention multiple services
- "Big bang" releases despite microservice architecture

**Code patterns:**
```typescript
// Service A importing types from Service B
import { UserDTO } from '@service-b/types';  // ❌ Tight coupling

// REST calls that look like function calls
const result = await serviceB.processUser(user);  // ❌ Sync dependency
await serviceC.updateStatus(result.id);           // ❌ Call chain

// Retry loops indicating fragile dependencies
for (let i = 0; i < 5; i++) {
  try {
    await serviceB.process(data);
    break;
  } catch (e) {
    await sleep(1000 * i);
  }
}
```

**Grep patterns:**
```bash
# Find cross-service imports
grep -r "from '@service-" --include="*.ts"
grep -r "import.*service" --include="*.py"

# Find synchronous service calls
grep -r "await.*Service\." --include="*.ts"
```

**Team signals:**
- Changes require coordinating multiple teams
- "Integration hell" before releases
- Shared library updates cascade across services

### Impact
- **Complexity**: Distributed debugging, no isolation benefits
- **Reliability**: Single service failure cascades
- **Deployment**: Can't deploy independently
- **Scale**: Can't scale services independently

### Resolution
1. **Identify coupling points** - Map service dependencies
2. **Introduce async communication** - Events instead of sync calls
3. **Define clear boundaries** - Service contracts, no shared types
4. **Allow data duplication** - Each service owns its data
5. **Apply strangler pattern** - Gradually decouple

---

## Chatty I/O

### Description
Making many small requests where fewer larger requests would work. Kills performance, especially over network.

### Detection Heuristics

**Code patterns:**
```python
# ❌ N+1 query problem
users = get_all_users()
for user in users:
    orders = get_orders_for_user(user.id)  # Query per user!
    process(user, orders)

# ❌ Many small API calls
for item_id in item_ids:
    item = await fetch_item(item_id)  # Call per item!
    items.append(item)
```

**Database signals:**
- Many similar queries in logs
- N+1 patterns visible in ORM output
- High query count, low data volume

**Network signals:**
- Many small HTTP requests to same service
- High latency despite low data transfer
- Connection pool exhaustion

**Grep patterns:**
```bash
# Find loops with await/fetch inside
grep -B2 -A2 "for.*in\|forEach" --include="*.ts" | grep -A3 "await\|fetch"

# Find potential N+1 in ORMs
grep -r "\.find\|\.get" --include="*.py" | grep -B1 "for "
```

### Impact
- **Performance**: Latency multiplied by call count
- **Resources**: Connection/thread exhaustion
- **Cost**: Higher cloud/API costs
- **Reliability**: More chances for failure

### Resolution
1. **Batch requests** - Combine multiple calls into one
2. **Use bulk APIs** - `getItems(ids)` instead of loop
3. **Eager loading** - ORM `include`/`join` to preload relations
4. **Caching** - Cache to avoid repeated requests
5. **GraphQL/DataLoader** - Batch at query level

---

## Premature Optimization

### Description
Optimizing before understanding actual bottlenecks. Wastes time, adds complexity, often optimizes wrong things.

### Detection Heuristics

**Code smells:**
- Complex caching with no performance data
- "Optimization" comments without benchmarks
- Micro-optimizations in non-hot paths
- Custom data structures instead of standard library

**Conversation signals:**
- "This will be slow" without profiling
- "We need to optimize for scale" at MVP stage
- Architecture decisions based on hypothetical load

**Code patterns:**
```python
# ❌ Premature caching
@cache(ttl=3600)  # Do we actually call this frequently?
def get_user_by_id(id):
    return db.query(User).get(id)

# ❌ Complex optimization without measurement
def process_items(items):
    # "Optimize" by batching in groups of 100
    # (Is this actually faster? Did we measure?)
    for batch in chunks(items, 100):
        process_batch(batch)
```

### Impact
- **Complexity**: Harder to understand and maintain
- **Time**: Effort spent on non-problems
- **Bugs**: Optimization often introduces bugs
- **Technical debt**: Optimized code harder to change

### Resolution
1. **Measure first** - Profile before optimizing
2. **Optimize hot paths** - Focus on actual bottlenecks
3. **Simple first** - Make it work, make it right, make it fast
4. **Benchmark changes** - Prove optimization helped

---

## Golden Hammer

### Description
Using familiar tool/pattern for everything, regardless of fit. "When all you have is a hammer, everything looks like a nail."

### Detection Heuristics

**Signals:**
- Same technology used for all problems
- Force-fitting patterns to unnatural use cases
- Ignoring better alternatives because team "knows" current tool
- Every new feature uses same architecture

**Examples:**
- Using relational DB for time-series data
- Using Kafka for simple request-response
- Using microservices for 3-person team
- Using GraphQL for simple REST APIs

**Team signals:**
- "We always use X" without evaluating fit
- New hires with better alternatives shut down
- No recent evaluation of tool choices

### Impact
- **Efficiency**: Wrong tool = more work
- **Performance**: Suboptimal for the use case
- **Learning**: Team doesn't grow skills
- **Innovation**: Missed opportunities

### Resolution
1. **Document decision rationale** - Why this tool?
2. **Regular tech evaluations** - Is this still the right choice?
3. **Prototype alternatives** - Try before committing
4. **Match tool to problem** - Right tool for the job

---

## Spaghetti Code

### Description
Code with complex, tangled control flow. Hard to follow, harder to modify, impossible to test.

### Detection Heuristics

**Code smells:**
- Deep nesting (> 3-4 levels)
- Long methods (> 50-100 lines)
- Many conditionals in sequence
- goto-like control flow (breaks, continues, early returns scattered)
- Unclear variable names

**Metric signals:**
- High cyclomatic complexity
- Low code coverage (hard to test)
- Many bug fixes in same area

**Grep patterns:**
```bash
# Find deeply nested code
grep -n "^        if\|^            if" --include="*.py"

# Find long functions
awk '/^def /{name=$2; start=NR} /^def /&&NR-start>50{print name, start, NR-start}' file.py
```

### Impact
- **Understanding**: Takes long to comprehend
- **Bugs**: Easy to introduce errors
- **Testing**: Hard to cover all paths
- **Maintenance**: Changes are risky

### Resolution
1. **Extract methods** - Break into small functions
2. **Reduce nesting** - Guard clauses, early returns
3. **Use polymorphism** - Replace conditionals with objects
4. **Write tests first** - Forces modular design

---

## Vendor Lock-In

### Description
Deep dependency on specific vendor's proprietary features, making migration extremely difficult.

### Detection Heuristics

**Code signals:**
- Direct use of vendor SDKs throughout codebase
- No abstraction layer over external services
- Proprietary query languages embedded everywhere
- Vendor-specific annotations/decorators

**Infrastructure signals:**
- Heavy use of managed services with no standard alternative
- Data in proprietary formats
- Workflows tied to vendor-specific features

**Cost signals:**
- Significant costs if vendor raises prices
- Migration estimates in months/years
- Business critical features only on one platform

### Impact
- **Flexibility**: Can't switch vendors easily
- **Cost**: Negotiating power limited
- **Risk**: Vendor shutdown/changes affect you
- **Innovation**: Limited to vendor's roadmap

### Resolution
1. **Abstraction layers** - Interface over vendor SDKs
2. **Standard formats** - Use portable data formats
3. **Multi-cloud design** - Avoid proprietary features
4. **Exit strategy** - Document migration path

---

## Lava Flow

### Description
Dead code or obsolete architecture that nobody understands but everyone's afraid to remove. Hardened from past experiments.

### Detection Heuristics

**Code signals:**
- Code with comments like "don't remove" or "legacy"
- Functions that appear unused but nobody removes
- Multiple ways to do the same thing (old + new)
- Deprecated but not removed features

**Historical signals:**
- Original authors left the team
- No documentation on why code exists
- Tests are disabled or skipped
- Code hasn't been modified in years

**Grep patterns:**
```bash
# Find potentially dead code
grep -r "TODO.*remove\|deprecated\|legacy\|unused" --include="*.py"

# Find old code not recently modified
find . -name "*.py" -mtime +365
```

### Impact
- **Maintenance**: Burden to maintain dead code
- **Understanding**: Confuses new developers
- **Bugs**: Dead code can be accidentally triggered
- **Builds**: Slows compilation, increases bundle

### Resolution
1. **Identify dead code** - Static analysis, coverage tools
2. **Document before removing** - Understand why it exists
3. **Remove incrementally** - Feature flags, gradual deletion
4. **Prevent recurrence** - CI checks for dead code

---

## Big Ball of Mud

### Description
System with no recognizable architecture. Unstructured, sprawling mess that evolved without planning.

### Detection Heuristics

**Structural signals:**
- No clear module/package organization
- Any file can import any other file
- No separation of concerns visible
- Inconsistent naming conventions

**Dependency signals:**
- Circular dependencies everywhere
- Import graphs are tangled mess
- No clear layers or boundaries

**Team signals:**
- "Only Bob knows how that works"
- Fear of changes breaking things
- New features take increasingly longer
- "We'll refactor it someday"

### Impact
- **Velocity**: Development slows over time
- **Quality**: Bug rate increases
- **Onboarding**: New developers struggle
- **Scale**: Can't grow team effectively

### Resolution
1. **Identify boundaries** - Find natural seams
2. **Establish conventions** - Naming, organization standards
3. **Incremental restructuring** - Strangler fig pattern
4. **Prevent new mud** - Architecture reviews, guidelines

---

## Analysis Paralysis

### Description
Over-analyzing decisions, never making progress. Seeking perfect solution instead of good-enough.

### Detection Heuristics

**Process signals:**
- Weeks of meetings before any code written
- Multiple competing designs with no decision
- Constant revisiting of decided items
- "We need more research" loops

**Team signals:**
- Design documents with no implementation
- Prototypes that are thrown away and restarted
- Key stakeholders can't agree
- Risk aversion dominates discussions

### Impact
- **Delivery**: Missed deadlines and opportunities
- **Morale**: Team frustrated by lack of progress
- **Learning**: No feedback from real usage
- **Competition**: Competitors ship while you debate

### Resolution
1. **Timebox decisions** - Deadline for architectural choices
2. **Good enough first** - Ship and iterate
3. **Define decision criteria** - Clear evaluation framework
4. **Reversibility analysis** - How hard to change later?

---

## Quick Reference Table

| Anti-Pattern | Key Signal | Primary Impact | Quick Fix |
|--------------|------------|----------------|-----------|
| God Object | Class > 500 lines, too many responsibilities | Maintenance | Extract classes |
| Distributed Monolith | Deploy together, shared DB | Deployment, reliability | Async communication |
| Chatty I/O | Loops with await/fetch | Performance | Batch operations |
| Premature Optimization | Optimization without profiling | Complexity | Measure first |
| Golden Hammer | Same tech for everything | Efficiency | Evaluate alternatives |
| Spaghetti Code | Deep nesting, long functions | Understanding | Extract methods |
| Vendor Lock-In | No abstraction over vendor | Flexibility | Add interfaces |
| Lava Flow | Dead code nobody removes | Maintenance | Delete incrementally |
| Big Ball of Mud | No architecture | Velocity | Find boundaries |
| Analysis Paralysis | Endless design, no code | Delivery | Timebox decisions |
