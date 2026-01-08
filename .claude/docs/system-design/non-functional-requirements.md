# Non-Functional Requirements Guide

Elicitation guide for gathering non-functional requirements (NFRs) during system design. NFRs define HOW the system should behave, not WHAT it should do.

---

## Quick NFR Categories

| Category | Key Questions | Units |
|----------|---------------|-------|
| Performance | How fast? How responsive? | ms, req/sec |
| Scalability | How much growth? What load? | users, TPS, TB |
| Availability | How much uptime? Recovery time? | %, minutes |
| Security | Who can access? How protected? | auth levels, encryption |
| Reliability | How often can it fail? Data loss? | MTBF, error rate |
| Maintainability | How easy to change? Deploy? | hours, complexity |

---

## 1. Performance Requirements

### Questions to Ask

**Response Time:**
- What's acceptable response time for user-facing operations?
- What about background/batch operations?
- Are there different tiers? (e.g., reads vs writes)

**Throughput:**
- How many concurrent users?
- Peak requests per second?
- What's the read/write ratio?

**Latency Distribution:**
- What's acceptable p50? p95? p99?
- Are there operations where latency spikes are unacceptable?

### Elicitation Framework

```
Response Time Goals:
┌────────────────────────────────────────────────────┐
│ Operation Type      │ Target  │ Max Acceptable     │
├────────────────────────────────────────────────────┤
│ Page load           │ < 200ms │ < 1s              │
│ API response        │ < 100ms │ < 500ms           │
│ Search              │ < 300ms │ < 2s              │
│ Batch processing    │ < 1hr   │ < 4hr             │
└────────────────────────────────────────────────────┘
```

### Default Targets (if not specified)

| Tier | p50 | p95 | p99 |
|------|-----|-----|-----|
| Real-time (trading, gaming) | < 10ms | < 50ms | < 100ms |
| Interactive (web apps) | < 100ms | < 300ms | < 1s |
| Responsive (dashboards) | < 500ms | < 2s | < 5s |
| Background (reports) | < 30s | < 2min | < 10min |

### Red Flags
- "As fast as possible" (need specific targets)
- No distinction between read/write operations
- Ignoring p99 (tail latency matters)
- Batch requirements not specified

---

## 2. Scalability Requirements

### Questions to Ask

**Growth Expectations:**
- Expected users in 1 year? 3 years?
- Data growth rate?
- Traffic patterns (steady, bursty, seasonal)?

**Scaling Dimensions:**
- What needs to scale independently?
- Horizontal vs vertical preferences?
- Budget constraints on scaling?

**Limits:**
- Maximum concurrent users?
- Maximum data retention?
- Geographic distribution needs?

### Elicitation Framework

```
Capacity Planning:
┌────────────────────────────────────────────────────┐
│ Metric              │ Current │ 1 Year │ 3 Year   │
├────────────────────────────────────────────────────┤
│ Users (DAU)         │         │        │          │
│ Requests/sec (peak) │         │        │          │
│ Data storage        │         │        │          │
│ Bandwidth           │         │        │          │
└────────────────────────────────────────────────────┘
```

### Default Targets

| Scale | Users | Requests/sec | Data |
|-------|-------|--------------|------|
| Small | < 1K DAU | < 100 | < 10GB |
| Medium | 1K-100K DAU | 100-10K | 10GB-1TB |
| Large | 100K-10M DAU | 10K-1M | 1TB-100TB |
| Massive | > 10M DAU | > 1M | > 100TB |

### Red Flags
- No growth projections
- "Infinite scale" expectations
- Ignoring data growth (often fastest growing)
- No budget for scaling discussed

---

## 3. Availability Requirements

### Questions to Ask

**Uptime:**
- Required uptime percentage?
- Planned maintenance windows acceptable?
- What constitutes "down"? (full outage vs degraded)

**Recovery:**
- Maximum acceptable downtime (RTO)?
- How much data loss acceptable (RPO)?
- Is partial functionality acceptable during recovery?

**Redundancy:**
- Multi-region required?
- Active-active vs active-passive?
- Failover automation level?

### Elicitation Framework

```
Availability Targets:
┌────────────────────────────────────────────────────┐
│ Tier          │ Uptime  │ Downtime/Year │ RTO     │
├────────────────────────────────────────────────────┤
│ Critical      │ 99.99%  │ 52 minutes    │ < 5 min │
│ High          │ 99.9%   │ 8.7 hours     │ < 1 hr  │
│ Standard      │ 99.5%   │ 1.8 days      │ < 4 hr  │
│ Best effort   │ 99%     │ 3.6 days      │ < 24 hr │
└────────────────────────────────────────────────────┘
```

### Default Targets

| Tier | Uptime | Downtime/Month | Typical Use |
|------|--------|----------------|-------------|
| Five 9s | 99.999% | 26 seconds | Payment, emergency |
| Four 9s | 99.99% | 4.3 minutes | Banking, healthcare |
| Three 9s | 99.9% | 43 minutes | Most SaaS |
| Two 9s | 99% | 7 hours | Internal tools |

### Red Flags
- "100% uptime" expectation (impossible)
- No RTO/RPO defined
- Availability requirements exceed budget
- No degraded mode consideration

---

## 4. Security Requirements

### Questions to Ask

**Authentication:**
- What authentication methods? (password, MFA, SSO)
- Session management requirements?
- Password policies?

**Authorization:**
- Role-based access control?
- Resource-level permissions?
- Multi-tenancy requirements?

**Data Protection:**
- Data classification levels?
- Encryption at rest? In transit?
- PII handling requirements?

**Compliance:**
- Regulatory requirements? (GDPR, HIPAA, SOC2, PCI)
- Audit logging requirements?
- Data residency requirements?

### Elicitation Framework

```
Security Posture:
┌────────────────────────────────────────────────────┐
│ Area              │ Requirement    │ Standard     │
├────────────────────────────────────────────────────┤
│ Authentication    │                │ OAuth2/OIDC  │
│ Authorization     │                │ RBAC         │
│ Encryption rest   │                │ AES-256      │
│ Encryption transit│                │ TLS 1.3      │
│ Compliance        │                │              │
└────────────────────────────────────────────────────┘
```

### Default Security Minimums

| Control | Minimum | Best Practice |
|---------|---------|---------------|
| Auth | Username/password | MFA, SSO |
| Password | 8 chars, complexity | 12+ chars, breach check |
| Encryption transit | TLS 1.2 | TLS 1.3 |
| Encryption rest | AES-128 | AES-256 |
| Session | 24hr timeout | 15min idle, absolute timeout |
| Audit | Login events | All data access |

### Red Flags
- "Security is important" without specifics
- No compliance requirements identified
- Assuming encryption handles everything
- No data classification

---

## 5. Reliability Requirements

### Questions to Ask

**Error Handling:**
- Acceptable error rate?
- What errors are acceptable vs unacceptable?
- Retry and compensation requirements?

**Data Integrity:**
- Consistency requirements? (strong vs eventual)
- Data validation requirements?
- Corruption detection and recovery?

**Fault Tolerance:**
- What failures must be tolerated?
- Graceful degradation requirements?
- Blast radius limitations?

### Elicitation Framework

```
Reliability Targets:
┌────────────────────────────────────────────────────┐
│ Metric           │ Target      │ Critical Path    │
├────────────────────────────────────────────────────┤
│ Error rate       │ < 0.1%      │ < 0.01%         │
│ Data consistency │ Eventual    │ Strong          │
│ MTBF            │ > 30 days   │ > 90 days       │
│ Retry success   │ > 95%       │ > 99%           │
└────────────────────────────────────────────────────┘
```

### Default Targets

| Metric | Standard | High Reliability |
|--------|----------|------------------|
| Error rate | < 1% | < 0.1% |
| Data loss | < 0.01% | Zero |
| MTBF | 7 days | 30+ days |
| Retry success | 90% | 99% |

### Red Flags
- No error budget defined
- "Zero errors" expectation
- Consistency requirements not aligned with availability
- No graceful degradation plan

---

## 6. Maintainability Requirements

### Questions to Ask

**Deployment:**
- Deployment frequency? (daily, weekly, monthly)
- Zero-downtime deployment required?
- Rollback requirements?

**Observability:**
- Monitoring requirements?
- Logging retention?
- Alerting requirements?

**Operations:**
- On-call requirements?
- Documentation standards?
- Incident response SLAs?

### Elicitation Framework

```
Operational Requirements:
┌────────────────────────────────────────────────────┐
│ Aspect           │ Requirement    │ Standard       │
├────────────────────────────────────────────────────┤
│ Deploy frequency │                │ Weekly         │
│ Deploy downtime  │                │ Zero           │
│ Log retention    │                │ 30 days        │
│ Alert response   │                │ < 15 min       │
│ Doc coverage     │                │ All endpoints  │
└────────────────────────────────────────────────────┘
```

### Default Targets

| Aspect | Startup | Enterprise |
|--------|---------|------------|
| Deploy frequency | Daily+ | Weekly |
| Log retention | 7 days | 90+ days |
| Metrics retention | 30 days | 1+ year |
| Alert response | 1 hour | 15 min |

### Red Flags
- No deployment strategy
- No observability requirements
- "We'll add monitoring later"
- No incident response plan

---

## NFR Prioritization Matrix

Use this to prioritize when requirements conflict:

```
                    High Importance
                          │
     Security ────────────┼──────────── Performance
                          │
                          │
     Reliability ─────────┼──────────── Scalability
                          │
                          │
     Availability ────────┼──────────── Cost
                          │
                    Low Importance
```

### Priority Framework

| Priority | Category | Reasoning |
|----------|----------|-----------|
| 1 | Security | Non-negotiable, breach = business end |
| 2 | Availability | Users can't use what's down |
| 3 | Performance | Slow = unusable for users |
| 4 | Reliability | Data integrity is trust |
| 5 | Scalability | Growth is good problem |
| 6 | Maintainability | Long-term concern |

---

## NFR Documentation Template

```markdown
## Non-Functional Requirements: [System Name]

### 1. Performance
- **Response Time**: [target p50/p95/p99]
- **Throughput**: [requests/sec, concurrent users]
- **Latency Budget**: [breakdown by component]

### 2. Scalability
- **Current Load**: [baseline metrics]
- **Growth Target**: [1yr, 3yr projections]
- **Scaling Strategy**: [horizontal/vertical approach]

### 3. Availability
- **Uptime Target**: [percentage, e.g., 99.9%]
- **RTO**: [recovery time objective]
- **RPO**: [recovery point objective]
- **Maintenance Window**: [if any]

### 4. Security
- **Authentication**: [method]
- **Authorization**: [model - RBAC, ABAC]
- **Encryption**: [at rest, in transit]
- **Compliance**: [standards - SOC2, GDPR, etc.]

### 5. Reliability
- **Error Rate Target**: [percentage]
- **Consistency Model**: [strong/eventual]
- **Fault Tolerance**: [what failures tolerated]

### 6. Maintainability
- **Deployment**: [frequency, strategy]
- **Monitoring**: [tools, coverage]
- **Documentation**: [standards]

### Priorities
1. [Most critical NFR]
2. [Second priority]
3. [Third priority]

### Tradeoffs Accepted
- [NFR X may be sacrificed for NFR Y because...]
```

---

## Quick Checklist

Before design is complete, verify:

- [ ] Performance targets defined with percentiles
- [ ] Scalability projections for 1 and 3 years
- [ ] Availability SLA with RTO/RPO
- [ ] Security requirements documented
- [ ] Compliance requirements identified
- [ ] Error budgets defined
- [ ] Observability requirements specified
- [ ] Deployment strategy defined
- [ ] Priority order established
- [ ] Tradeoffs explicitly documented
