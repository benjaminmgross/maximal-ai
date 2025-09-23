# Implement

You are tasked with implementing an approved technical plan. These plans contain phases with specific changes and success criteria.

## Getting Started

When given a plan path:
- Read the plan completely and check for any existing checkmarks (- [x])
- Read any original research documents mentioned in the plan
- **Read files fully** - never use limit/offset parameters, you need complete context
- Think deeply about how the pieces fit together
- Create a todo list to track your progress
- Start implementing if you understand what needs to be done

If no plan path provided, ask for one.

## Implementation Philosophy

Plans are carefully designed, but reality can be messy. Your job is to:
- Follow the plan's intent while adapting to what you find
- Implement each phase fully before moving to the next
- Verify your work makes sense in the broader codebase context
- Update checkboxes in the plan as you complete sections

When things don't match the plan exactly, think about why and communicate clearly. The plan is your guide, but your judgment matters too.

If you encounter a mismatch:
- STOP and think deeply about why the plan can't be followed
- Present the issue clearly:
  ```
  Issue in Phase [N]:
  Expected: [what the plan says]
  Found: [actual situation]
  Why this matters: [explanation]
  
  How should I proceed?
  ```

## Implementation Process

### Step 1: Preparation
1. Read the entire plan to understand the full scope
2. Note any phases already marked complete
3. Read all files mentioned in the plan FULLY
4. Create a TodoWrite list with:
   - One item for each phase
   - Sub-items for major changes within each phase
   - Items for verification steps

### Step 2: Phase-by-Phase Implementation
For each phase:

1. **Understand the Goal**
   - Re-read the phase overview
   - Understand what this phase accomplishes
   - Review the success criteria

2. **Make the Changes**
   - Implement changes in the order specified
   - Follow the code examples closely
   - Adapt to actual code structure as needed
   - Commit frequently (if user requests)

3. **Verify as You Go**
   - Run automated verification commands after each major change
   - Fix issues immediately before proceeding
   - Don't accumulate technical debt

4. **Update Progress**
   - Check off completed items in the plan using Edit
   - Update your TodoWrite list
   - Note any deviations from the plan

### Step 3: Verification Approach

After implementing a phase:
- Run all automated success criteria checks
- Usually `make check test` or similar covers everything
- Fix any issues before proceeding
- Update your progress in both the plan and your todos
- Check off completed items in the plan file itself using Edit

Don't let verification interrupt your flow - batch it at natural stopping points.

### Step 4: Phase Completion

Before moving to the next phase:
1. Ensure all automated verification passes
2. Update the plan with checkmarks for completed items
3. Document any significant deviations
4. Commit your changes if appropriate

## Handling Issues

### When Tests Fail
1. Read the error message carefully
2. Understand what the test expects
3. Fix the implementation, not the test (unless the test is wrong)
4. Re-run verification

### When the Plan Doesn't Match Reality
1. Determine if the codebase has changed since planning
2. Assess if the plan's intent can still be achieved
3. Present the mismatch clearly to the user
4. Propose an adaptation that maintains the plan's goals

### When You Need More Context
Use sub-agents sparingly for:
- Targeted debugging of specific issues
- Exploring unfamiliar parts of the codebase
- Finding examples of similar implementations

## Progress Tracking

Maintain clear progress indicators:
- Use TodoWrite to track implementation tasks
- Update plan checkboxes as you complete sections
- Provide periodic status updates for long implementations
- Note any blockers or concerns immediately

## If You Get Stuck

When something isn't working as expected:
- First, make sure you've read and understood all the relevant code
- Consider if the codebase has evolved since the plan was written
- Present the mismatch clearly and ask for guidance
- Don't waste time on approaches that clearly won't work

## Resuming Work

If the plan has existing checkmarks:
- Trust that completed work is done
- Pick up from the first unchecked item
- Verify previous work only if something seems off
- Don't re-implement completed phases

## Implementation Best Practices

1. **Follow the Plan's Structure**
   - Implement phases in order
   - Complete each phase fully before moving on
   - Don't jump ahead even if you see the solution

2. **Maintain Code Quality**
   - Follow existing code patterns
   - Keep consistent style
   - Add appropriate error handling
   - Don't introduce new dependencies without approval

3. **Test Continuously**
   - Run tests after each significant change
   - Don't accumulate failing tests
   - Fix breaks immediately

4. **Communicate Progress**
   - Update todos regularly
   - Check off plan items as completed
   - Report blockers immediately
   - Note any concerns or uncertainties

## Success Indicators

You know you're doing well when:
- Tests pass after each phase
- The code follows existing patterns
- You're making steady progress through the plan
- You catch issues early and fix them
- The implementation matches the plan's intent

## Common Pitfalls to Avoid

- Don't skip reading files fully
- Don't assume the plan is perfect - adapt as needed
- Don't accumulate technical debt
- Don't implement multiple phases without verification
- Don't ignore failing tests
- Don't make changes outside the plan's scope

## Final Checklist

Before declaring implementation complete:
- [ ] All phases implemented
- [ ] All automated verification passing
- [ ] Plan updated with completion checkmarks
- [ ] Any deviations documented
- [ ] Code follows project conventions
- [ ] No commented-out code or TODOs left
- [ ] All tests passing

Remember: You're implementing a solution, not just checking boxes. Keep the end goal in mind and maintain forward momentum.