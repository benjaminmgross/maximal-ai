# Tradeoff Decision Trees

Decision frameworks for common architectural choices. Use these to systematically evaluate options based on your specific context.

---

## SQL vs NoSQL

### Decision Factors

| Factor | Favors SQL | Favors NoSQL |
|--------|-----------|--------------|
| Data structure | Structured, relational | Flexible, nested, variable |
| Query patterns | Complex joins, aggregations | Simple lookups, key-value |
| Consistency needs | Strong consistency required | Eventual consistency OK |
| Scale pattern | Vertical scaling sufficient | Horizontal scaling needed |
| Schema evolution | Stable, rarely changes | Frequent schema changes |
| Transactions | Multi-table ACID required | Single-document operations |
| Data volume | Moderate (TBs) | Massive (PBs) |

### Decision Tree

```
1. Do you need ACID transactions across multiple tables?
   ├── YES → SQL (PostgreSQL, MySQL)
   └── NO → Continue...

2. Is your data highly relational (many-to-many relationships)?
   ├── YES → SQL
   └── NO → Continue...

3. Do you need complex queries with joins, aggregations?
   ├── YES → SQL
   └── NO → Continue...

4. Is horizontal scaling to 100+ nodes required?
   ├── YES → Consider NoSQL (Cassandra, DynamoDB)
   └── NO → Continue...

5. Is schema flexibility critical (documents vary in structure)?
   ├── YES → Document store (MongoDB, DynamoDB)
   └── NO → Continue...

6. Is your data time-series or event-based?
   ├── YES → Time-series DB (TimescaleDB, InfluxDB)
   └── NO → SQL is likely simpler and sufficient
```

### Context-Specific Guidance

**Startups:**
- Start with PostgreSQL (versatile, well-understood)
- Migrate if you hit scale limits
- Don't prematurely optimize for scale you don't have

**E-commerce:**
- SQL for orders, transactions (ACID needed)
- NoSQL for product catalog (flexible attributes)
- Redis for session, cart (speed critical)

**Analytics:**
- SQL/columnar for ad-hoc queries (BigQuery, Redshift)
- Time-series for metrics (InfluxDB, TimescaleDB)
- NoSQL for raw event ingestion

**IoT/Real-time:**
- Time-series for sensor data
- NoSQL for device metadata
- SQL for business analytics

---

## Monolith vs Microservices

### Decision Factors

| Factor | Favors Monolith | Favors Microservices |
|--------|-----------------|----------------------|
| Team size | < 10 developers | > 20 developers |
| Deployment | Simple, single unit | Independent per team |
| Scale | Uniform scaling | Per-service scaling |
| Tech diversity | Single stack | Polyglot acceptable |
| Latency | Sub-millisecond internal calls | Network latency OK |
| Domain boundaries | Unclear, evolving | Clear, stable |
| DevOps capability | Limited | Strong |

### Decision Tree

```
1. How many developers will work on this?
   ├── < 10 → Lean toward monolith
   ├── 10-30 → Consider modular monolith first
   └── > 30 → Microservices may help with coordination

2. Can you define clear, stable service boundaries?
   ├── YES → Microservices viable
   └── NO → Monolith (or modular monolith) until clearer

3. Do different components need different scaling?
   ├── YES (significantly) → Microservices
   └── NO → Monolith simpler

4. Do you have strong DevOps/platform capability?
   ├── YES → Microservices manageable
   └── NO → Monolith until ops mature

5. Is independent deployment per team critical?
   ├── YES → Microservices
   └── NO → Monolith may be sufficient

6. Is sub-millisecond latency between components critical?
   ├── YES → Monolith (network latency unavoidable in microservices)
   └── NO → Either works
```

### Evolution Path

```
Monolith → Modular Monolith → Microservices

1. Start monolith: Fast iteration, low overhead
2. Establish modules: Clear boundaries within monolith
3. Extract services: When boundaries proven stable
4. Only go distributed when benefits outweigh costs
```

### Warning Signs

**Don't choose microservices if:**
- Team < 10 people (overhead not worth it)
- MVP/startup phase (need to iterate fast)
- Domain not well understood (boundaries will be wrong)
- No CI/CD pipeline (deployment will be painful)

**Don't choose monolith if:**
- Teams need to deploy independently
- Vastly different scaling requirements per feature
- Technology diversity is required
- Teams > 30 and stepping on each other

---

## Synchronous vs Asynchronous Communication

### Decision Factors

| Factor | Favors Sync | Favors Async |
|--------|-------------|--------------|
| Latency requirement | Immediate response needed | Delay acceptable |
| Consistency | Strong consistency required | Eventual consistency OK |
| Failure handling | Must succeed or fail atomically | Retry/recovery OK |
| Throughput | Moderate | High volume |
| Coupling | Coupling acceptable | Loose coupling desired |

### Decision Tree

```
1. Does the caller need an immediate response?
   ├── YES → Continue to check sync viability
   └── NO → Async (fire-and-forget, queue, events)

2. Is strong consistency required?
   ├── YES → Sync (or saga for distributed TX)
   └── NO → Async with eventual consistency

3. Is the downstream service critical path?
   ├── YES → Sync with circuit breaker
   └── NO → Async, don't block caller

4. Is there high volume (> 1000 req/sec)?
   ├── YES → Async queue to handle backpressure
   └── NO → Sync may be fine

5. Should caller wait if downstream slow?
   ├── YES → Sync with timeout
   └── NO → Async with callback/webhook
```

### Common Patterns

**User-facing APIs:** Usually sync (user waiting)
- Add timeouts and circuit breakers
- Consider async for long operations + polling/webhook

**Service-to-service:** Often async (loose coupling)
- Events for broadcasts (one-to-many)
- Queues for reliable delivery
- Sync only for request-response with low latency needs

**Background jobs:** Always async
- Use queues (SQS, RabbitMQ, Celery)
- Implement retry and dead-letter handling

---

## REST vs GraphQL vs gRPC

### Decision Factors

| Factor | REST | GraphQL | gRPC |
|--------|------|---------|------|
| Client control | Low (fixed responses) | High (client specifies) | Low |
| Caching | Easy (HTTP caching) | Complex | Complex |
| Performance | Good | Variable | Excellent |
| Type safety | Manual (OpenAPI) | Schema-based | Strong (Protobuf) |
| Use case | Public APIs, CRUD | Flexible queries, BFF | Internal microservices |
| Learning curve | Low | Medium | High |

### Decision Tree

```
1. Is this a public API for external consumers?
   ├── YES → REST (well-understood, tooling)
   └── NO → Continue...

2. Do different clients need different data shapes?
   ├── YES → GraphQL (flexible queries)
   └── NO → Continue...

3. Is this internal service-to-service communication?
   ├── YES → gRPC (performance, type safety)
   └── NO → Continue...

4. Is HTTP caching important?
   ├── YES → REST
   └── NO → Continue...

5. Do you need real-time subscriptions?
   ├── YES → GraphQL or WebSockets
   └── NO → REST is simplest default
```

### Context-Specific Guidance

**Mobile apps:** GraphQL
- Minimize data transfer (request only needed fields)
- Handle varying screen sizes with different queries
- Single endpoint simplifies networking

**Microservices:** gRPC
- Binary protocol = fast
- Strong types = fewer bugs
- Streaming support

**Public APIs:** REST
- Universal understanding
- HTTP caching
- OpenAPI documentation

**BFF pattern:** GraphQL
- Aggregate multiple backend calls
- Client-specific queries

---

## Strong vs Eventual Consistency

### Decision Factors

| Factor | Favors Strong | Favors Eventual |
|--------|---------------|-----------------|
| Data type | Financial, inventory | Social, analytics |
| User expectation | See own writes immediately | Some lag acceptable |
| Scale | Moderate | Massive |
| Availability | Consistency > availability | Availability > consistency |
| Geography | Single region | Multi-region |

### Decision Tree

```
1. Is this financial/inventory data where wrong reads cause harm?
   ├── YES → Strong consistency (ACID, single leader)
   └── NO → Continue...

2. Do users need to see their own writes immediately?
   ├── YES → Strong consistency or read-your-writes guarantee
   └── NO → Continue...

3. Is global, multi-region deployment required?
   ├── YES → Eventual consistency (latency constraint)
   └── NO → Continue...

4. Is availability more important than consistency?
   ├── YES → Eventual consistency
   └── NO → Strong consistency

5. Is this analytical/reporting data?
   ├── YES → Eventual consistency (slight delay OK)
   └── NO → Evaluate based on business requirements
```

### Hybrid Approach

Often you need both:
- **Strong:** User balances, inventory counts, session state
- **Eventual:** Feeds, notifications, analytics, recommendations

Use different data stores or consistency levels for different data types.

---

## Push vs Pull Architecture

### Decision Factors

| Factor | Favors Push | Favors Pull |
|--------|-------------|-------------|
| Data freshness | Real-time critical | Delay acceptable |
| Client count | Few, known clients | Many, dynamic clients |
| Data volume | Moderate | High (client filters) |
| Client availability | Always connected | Intermittent connection |
| Complexity | Higher (maintain connections) | Lower |

### Decision Tree

```
1. Is real-time data freshness critical?
   ├── YES → Push (WebSockets, SSE, push notifications)
   └── NO → Continue...

2. Do you have many clients with different data needs?
   ├── YES → Pull (client decides what/when)
   └── NO → Continue...

3. Are clients always connected?
   ├── YES → Push viable
   └── NO → Pull (with caching/offline support)

4. Is server push infrastructure available?
   ├── YES → Push if needed
   └── NO → Pull (simpler to implement)

5. Do clients need historical data too?
   ├── YES → Pull (or push + pull hybrid)
   └── NO → Push for current state
```

### Hybrid Patterns

**Push + Pull:**
- Push: Notify that data changed
- Pull: Client fetches actual data
- Benefits: Real-time notification, client controls fetch

**Long polling:**
- Client "pulls" but server holds request until data ready
- Compromise between push and pull

---

## Caching Strategy

### Decision Tree

```
1. Is data read much more than written (> 10:1)?
   ├── YES → Caching beneficial
   └── NO → May not be worth complexity

2. Is data latency-sensitive?
   ├── YES → In-memory cache (Redis, Memcached)
   └── NO → Continue...

3. Is cache miss expensive (slow query, external API)?
   ├── YES → Aggressive caching, warm cache
   └── NO → Simple TTL-based caching

4. Does data need global distribution?
   ├── YES → CDN for static, distributed cache for dynamic
   └── NO → Local cache may suffice

5. Is stale data acceptable?
   ├── YES → TTL-based expiration
   └── NO → Cache invalidation on write
```

### Cache Patterns

| Pattern | When to Use | Implementation |
|---------|-------------|----------------|
| Cache-aside | General purpose | App reads cache, writes to both |
| Read-through | Simplify app code | Cache handles DB reads |
| Write-through | Strong consistency | Cache writes to DB immediately |
| Write-behind | High write volume | Cache batches writes to DB |
| Refresh-ahead | Predictable access | Pre-refresh before expiry |

### Invalidation Strategies

| Strategy | Consistency | Complexity |
|----------|-------------|------------|
| TTL | Eventual | Low |
| Event-based | Strong | Medium |
| Version tags | Strong | Medium |
| Manual | Strong | High |

---

## Horizontal vs Vertical Scaling

### Decision Tree

```
1. Can you solve the problem with a bigger machine?
   ├── YES (and affordable) → Vertical first (simpler)
   └── NO → Need horizontal

2. Is the workload stateless?
   ├── YES → Horizontal straightforward
   └── NO → Need state management (shared cache, session affinity)

3. Is database the bottleneck?
   ├── YES → Read replicas (horizontal reads), sharding (horizontal writes)
   └── NO → Scale compute layer

4. Do you need fault tolerance (no single point of failure)?
   ├── YES → Horizontal (multiple instances)
   └── NO → Vertical may suffice

5. Is cost a concern?
   ├── YES → Horizontal (commodity hardware)
   └── NO → Vertical can be simpler
```

### Scaling Approach by Component

| Component | Vertical First | Horizontal When |
|-----------|---------------|-----------------|
| Web servers | More cores/RAM | Load balancer + instances |
| Databases | Bigger instance | Read replicas, sharding |
| Caches | More memory | Cluster (Redis Cluster) |
| Message queues | Bigger instance | Partitioning (Kafka) |
| Storage | Larger disks | Distributed storage |

---

## Quick Reference Matrix

| Decision | Default Choice | Switch When |
|----------|---------------|-------------|
| SQL vs NoSQL | SQL | Scale > vertical, flexible schema needed |
| Monolith vs Micro | Monolith | Teams > 20, clear boundaries, scaling needs differ |
| Sync vs Async | Sync | High volume, loose coupling, long operations |
| REST vs GraphQL | REST | Multiple clients, flexible queries needed |
| REST vs gRPC | REST | Internal microservices, performance critical |
| Strong vs Eventual | Strong | Global distribution, high availability needed |
| Push vs Pull | Pull | Real-time requirements |
| Vertical vs Horizontal | Vertical | Fault tolerance, cost, very high scale |
