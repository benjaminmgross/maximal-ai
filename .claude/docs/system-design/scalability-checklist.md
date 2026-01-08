# Scalability Assessment Checklist

Systematic checklist for identifying scalability concerns, bottlenecks, and improvement opportunities in existing systems.

---

## Quick Assessment Questions

Use these to quickly identify if deep analysis is needed:

1. **What's the current load vs capacity?** (If > 60%, investigate)
2. **What breaks first at 10x load?**
3. **Are there single points of failure?**
4. **What's the most expensive operation?**
5. **Where is data growing fastest?**

---

## Layer-by-Layer Analysis

### 1. Load Balancing & Entry Points

#### Questions
- [ ] Is there a load balancer in front of web servers?
- [ ] What's the load balancing algorithm? (round-robin, least connections, etc.)
- [ ] Are health checks configured?
- [ ] Is SSL termination at load balancer or app servers?
- [ ] Can load balancer handle the projected load?

#### Detection Commands
```bash
# Find load balancer configs
grep -r "upstream\|proxy_pass" nginx/
grep -r "load_balance\|health_check" config/

# Check for single entry point (potential SPOF)
grep -r "host:\|endpoint:" config/ | sort | uniq
```

#### Bottleneck Signals
- Single load balancer (SPOF)
- No health checks (unhealthy servers get traffic)
- SSL at app servers (CPU overhead)
- Session affinity forcing uneven distribution

#### Scaling Strategies
| Issue | Solution |
|-------|----------|
| Single LB | Multi-LB with DNS failover or cloud LB |
| Uneven distribution | Review balancing algorithm |
| SSL overhead | Terminate at LB, use HTTP internally |
| Session affinity | Externalize sessions (Redis) |

---

### 2. Application Servers

#### Questions
- [ ] How many app server instances?
- [ ] Are they stateless (can add more easily)?
- [ ] What's the CPU/memory utilization?
- [ ] What's the p99 response time?
- [ ] Is auto-scaling configured?

#### Detection Commands
```bash
# Find state in application
grep -r "session\|state\|singleton" src/

# Find global/static variables (potential state)
grep -r "static\|global\|class.*=" src/

# Find file-based operations (not horizontally scalable)
grep -r "fs\.\|open(\|write(" src/
```

#### Bottleneck Signals
- High CPU with low request volume (inefficient code)
- Memory growth over time (memory leaks)
- p99 >> p50 (some requests very slow)
- File system operations (can't share across instances)

#### Scaling Strategies
| Issue | Solution |
|-------|----------|
| CPU bound | Optimize hot paths, add instances |
| Memory bound | Fix leaks, larger instances, optimize |
| Stateful | Externalize to Redis/DB |
| File operations | Use object storage (S3), shared filesystem |

---

### 3. Database Layer

#### Questions
- [ ] What's the database type and version?
- [ ] What's the current storage size and growth rate?
- [ ] What's the query volume and distribution?
- [ ] Are there read replicas?
- [ ] What's the connection pool configuration?
- [ ] Are queries indexed appropriately?

#### Detection Commands
```bash
# Find N+1 query patterns
grep -r "\.find\|\.get\|SELECT" src/ | grep -B2 "for\|forEach"

# Find missing indexes (look for queries on non-PK columns)
grep -r "WHERE.*=" src/ --include="*.sql"

# Find connection creation (should use pool)
grep -r "connect\|create.*connection" src/
```

#### Bottleneck Signals
- High read latency → Missing indexes, no read replicas
- High write latency → Disk I/O, too many indexes
- Connection errors → Pool exhausted
- Growing query time → Data growth, missing indexes

#### Scaling Strategies
| Issue | Solution |
|-------|----------|
| Read heavy | Read replicas, query caching |
| Write heavy | Write-through cache, sharding |
| Large tables | Archiving, partitioning |
| Many connections | Connection pooling, PgBouncer |
| Complex queries | Materialized views, denormalization |

#### Index Checklist
- [ ] Primary keys on all tables
- [ ] Indexes on foreign keys
- [ ] Indexes on commonly filtered columns
- [ ] Composite indexes for multi-column queries
- [ ] No unnecessary indexes (write overhead)

---

### 4. Caching Layer

#### Questions
- [ ] What's being cached? (queries, sessions, API responses)
- [ ] What's the cache hit rate?
- [ ] What's the eviction policy?
- [ ] What's the cache size vs data size?
- [ ] How is cache invalidated?

#### Detection Commands
```bash
# Find caching usage
grep -r "cache\|redis\|memcache" src/

# Find potential cache candidates (repeated expensive operations)
grep -r "@cache\|\.cache\|cache\." src/
```

#### Bottleneck Signals
- Low hit rate (< 80%) → Wrong data cached, TTL too short
- High eviction → Cache too small
- Cache miss storms → No stampede protection
- Stale data issues → Invalidation not working

#### Scaling Strategies
| Issue | Solution |
|-------|----------|
| Low hit rate | Cache right data, adjust TTL |
| Cache too small | Increase size, shard cache |
| Miss storms | Stampede protection, warm cache |
| Stale data | Event-based invalidation |

---

### 5. External Services & APIs

#### Questions
- [ ] What external services are called?
- [ ] What's the timeout configuration?
- [ ] Is there retry logic?
- [ ] Are there circuit breakers?
- [ ] What happens when external service fails?

#### Detection Commands
```bash
# Find external HTTP calls
grep -r "fetch\|axios\|requests\.\|http\." src/

# Find API keys/endpoints (external dependencies)
grep -r "API_KEY\|api_url\|endpoint" config/

# Check for timeout configuration
grep -r "timeout" src/
```

#### Bottleneck Signals
- No timeouts → Requests hang indefinitely
- No retries → Transient failures cause errors
- No circuit breaker → Cascading failures
- Sync calls to slow APIs → Blocks threads

#### Scaling Strategies
| Issue | Solution |
|-------|----------|
| No timeouts | Add timeouts (reasonable defaults: 5-30s) |
| Transient failures | Retry with exponential backoff |
| Cascade failures | Circuit breaker pattern |
| Sync to slow APIs | Async processing, webhooks |

---

### 6. Message Queues & Async Processing

#### Questions
- [ ] What message queue is used?
- [ ] What's the queue depth/backlog?
- [ ] How many consumers?
- [ ] What's the processing rate vs ingestion rate?
- [ ] What happens to failed messages?

#### Detection Commands
```bash
# Find queue usage
grep -r "queue\|publish\|subscribe\|producer\|consumer" src/

# Find async job definitions
grep -r "@task\|worker\|job\|celery\|bull" src/
```

#### Bottleneck Signals
- Growing queue depth → Consumers too slow
- Message loss → No persistence, no DLQ
- Processing spikes → No rate limiting
- Duplicate processing → No idempotency

#### Scaling Strategies
| Issue | Solution |
|-------|----------|
| Queue backlog | Add consumers, optimize processing |
| Message loss | Enable persistence, DLQ |
| Processing spikes | Rate limiting, backpressure |
| Duplicates | Idempotent processing |

---

### 7. Data Storage & Files

#### Questions
- [ ] Where are files stored? (local, S3, etc.)
- [ ] What's the storage growth rate?
- [ ] Is there a retention policy?
- [ ] Are large files being served through app servers?
- [ ] Is there backup and recovery?

#### Detection Commands
```bash
# Find file operations
grep -r "fs\.\|open(\|write(\|save.*file" src/

# Find local path references
grep -r "'/tmp\|'/var\|'/data" src/

# Find large file serving
grep -r "send.*file\|download" src/
```

#### Bottleneck Signals
- Local file storage → Can't scale horizontally
- Files through app server → Wastes compute
- No retention → Storage grows forever
- No CDN → High latency for static assets

#### Scaling Strategies
| Issue | Solution |
|-------|----------|
| Local storage | Object storage (S3, GCS) |
| Files through app | Direct from S3 or CDN |
| Storage growth | Retention policies, archiving |
| Static asset latency | CDN (CloudFront, Fastly) |

---

## Single Points of Failure (SPOF)

### Checklist
- [ ] Single load balancer
- [ ] Single database (no replicas)
- [ ] Single cache instance
- [ ] Single message broker
- [ ] Single region deployment
- [ ] Single DNS provider
- [ ] Single payment provider
- [ ] Manual processes (single person)

### Detection
```bash
# Find hardcoded hosts (potential SPOF)
grep -r "host.*=\|hostname.*=" config/

# Find single instance configs
grep -r "replicas.*=.*1\|single\|master" config/
```

---

## Capacity Planning Questions

### Current State
1. What's the current request rate?
2. What's the p50/p95/p99 response time?
3. What's the error rate?
4. What percentage of capacity is used?

### Growth Projections
1. What's the expected load in 6 months? 1 year?
2. What components hit limits first?
3. What's the cost to scale each component?
4. What's the lead time to scale each component?

### Breaking Points
1. At what load does response time degrade?
2. At what load do errors spike?
3. At what point do costs become prohibitive?
4. What can't be scaled (architectural limits)?

---

## Quick Reference: Scaling Numbers

| Component | Good | Concern | Critical |
|-----------|------|---------|----------|
| CPU utilization | < 60% | 60-80% | > 80% |
| Memory utilization | < 70% | 70-85% | > 85% |
| Disk utilization | < 70% | 70-85% | > 85% |
| DB connections | < 60% pool | 60-80% | > 80% |
| Cache hit rate | > 90% | 80-90% | < 80% |
| Queue depth | Low/stable | Growing | High/growing |
| Error rate | < 0.1% | 0.1-1% | > 1% |
| p99 latency | < 500ms | 500ms-2s | > 2s |

---

## Output Template

Use this structure for scalability assessment reports:

```markdown
## Scalability Assessment: [System Name]

### Executive Summary
[2-3 sentences on overall scalability posture]

### Current Capacity
| Metric | Current | Capacity | Utilization |
|--------|---------|----------|-------------|
| Requests/sec | | | |
| Database connections | | | |
| Memory | | | |

### Bottlenecks Identified
1. **[Component]** - [Issue] - Severity: [High/Medium/Low]
2. ...

### Single Points of Failure
1. [Component] - [Impact if fails]
2. ...

### Recommendations
| Priority | Issue | Solution | Effort | Impact |
|----------|-------|----------|--------|--------|
| 1 | | | | |
| 2 | | | | |

### Growth Projections
At 10x current load:
- [Component A] fails at [X load]
- [Component B] needs [Y change]
```
