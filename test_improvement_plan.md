# RPI Workflow Improvement A/B Test

**Date**: 2025-11-11
**Test Objective**: Compare NEW RPI workflow (with clarifying questions + requirement artifacts) vs CURRENT RPI workflow

---

## Test Scenario 1: Multi-Repo Feature (Authentication)

**Feature Description**: Add OAuth authentication to minty_revamp that integrates with vrm_bridge_backend

**Test Steps**:

### A. Current Implementation (dev branch)
1. Run: `/research How does authentication work across minty_revamp and vrm_bridge_backend?`
2. Observe: Does it ask clarifying questions? (Expected: NO)
3. Count: How many questions did you need to answer? (Expected: 0-1)
4. Review research output: Check for "Integration Points" section (Expected: NO explicit section)
5. Review research output: Check for "Questions for Hardened Requirements" (Expected: "Open Questions" instead)
6. Note: Did research miss any critical integration points?

### B. New Implementation (feature/hl-mai-improvement branch)
1. Run: `/research How does authentication work across minty_revamp and vrm_bridge_backend?`
2. Observe: Does it ask clarifying questions? (Expected: YES, 2-4 questions)
3. Count: How many questions did you need to answer?
4. Review research output: Check for "Integration Points" section (Expected: YES with API calls, shared models)
5. Review research output: Check for "Questions for Hardened Requirements" (Expected: YES with checkboxes)
6. Note: Did research identify integration points that current missed?

### C. Comparison Metrics
- **Clarifying Questions**: Current [0] vs New [2-4]
- **Integration Points Identified**: Current [count] vs New [count]
- **Unanswered Questions Flagged**: Current [count] vs New [count]
- **Time to Complete Research**: Current [X min] vs New [Y min]
- **CTO Confidence in Research**: Current [1-10] vs New [1-10]

---

## Test Scenario 2: Single-Repo Bug Fix

**Bug Description**: Fix payment calculation error in minty_revamp checkout flow

**Test Steps**:

### A. Current Implementation
1. Run: `/research Why is payment calculation failing in checkout?`
2. Observe: Clarifying questions asked? (Expected: NO)
3. Review research output: Integration points section? (Expected: NO)
4. Note: Did research provide acceptance test specification?

### B. New Implementation
1. Run: `/research Why is payment calculation failing in checkout?`
2. Observe: Clarifying questions asked? (Expected: YES but minimal - bug fix is clearer scope)
3. Review research output: Integration points section? (Expected: YES or N/A if truly isolated)
4. Note: Did research provide acceptance test specification in hardened requirements?

### C. Comparison Metrics
- **Appropriate Question Volume**: Did new implementation skip unnecessary questions for clear bug? [YES/NO]
- **Acceptance Test Clarity**: Current [1-10] vs New [1-10]
- **Time Efficiency**: Current [X min] vs New [Y min]

---

## Test Scenario 3: Vague Feature Request

**Feature Description**: "Make the dashboard faster"

**Test Steps**:

### A. Current Implementation
1. Run: `/research Make the dashboard faster`
2. Observe: Does it ask clarifying questions before researching? (Expected: NO)
3. Note: Does research hallucinate or make incorrect assumptions?

### B. New Implementation
1. Run: `/research Make the dashboard faster`
2. Observe: Does it ask clarifying questions? (Expected: YES - which dashboard? what's slow? etc.)
3. Note: Does research produce more focused findings based on clarifications?

### C. Comparison Metrics
- **Assumption Count**: Current [count assumptions] vs New [count assumptions]
- **Research Relevance**: Current [1-10] vs New [1-10]
- **False Positives**: Current [count incorrect findings] vs New [count]

---

## Success Criteria for New Implementation

The new implementation is successful if:

1. **Clarifying Questions Work**:
   - [ ] Questions are asked BEFORE agent spawning
   - [ ] Questions are serial (one at a time)
   - [ ] Questions offer multiple choice when possible
   - [ ] Questions are skipped when appropriate (detailed spec provided)

2. **Requirement Artifacts Are Valuable**:
   - [ ] "Expected Repos Involved" correctly identifies primary and secondary repos
   - [ ] "Integration Points" maps cross-repo dependencies clearly
   - [ ] "Questions for Hardened Requirements" flags unknowns that would block implementation
   - [ ] Research output is more actionable for planning phase

3. **User Experience Improves**:
   - [ ] CTO feels more confident in research accuracy
   - [ ] Research catches integration issues earlier
   - [ ] Planning phase has fewer surprises
   - [ ] Overall time to working feature decreases (fewer implementation failures)

4. **No Degradation**:
   - [ ] Research doesn't take significantly longer
   - [ ] Questions aren't annoying or excessive
   - [ ] Research quality doesn't decrease for simple cases
