# Architectural Patterns Catalog

Reference guide for identifying and applying architectural patterns. Use this to understand when patterns are appropriate and how to detect them in existing codebases.

---

## Layered Architecture

### Description
Separates concerns into horizontal layers, each with specific responsibilities. Common layers: Presentation, Business Logic, Data Access, Infrastructure.

### When to Use
- Traditional enterprise applications
- Clear separation of concerns needed
- Teams organized by technical function
- Moderate complexity CRUD applications
- Well-understood domain with stable requirements

### When NOT to Use
- Highly event-driven systems
- Real-time processing requirements
- Microservices architecture (use domain layers instead)
- Rapid prototyping (overhead too high)

### Key Components
- **Presentation Layer**: UI, API controllers, request/response handling
- **Business Layer**: Domain logic, services, use cases
- **Data Access Layer**: Repositories, ORM, data mappers
- **Infrastructure**: External services, caching, messaging

### Detection Heuristics
**Signs it's in use:**
- Directory structure like `controllers/`, `services/`, `repositories/`
- Clear import direction (upper layers import lower layers only)
- Service classes with business logic, repositories for data

**Code patterns:**
```
controllers/ → services/ → repositories/ → database
       ↓           ↓            ↓
    DTOs      Domain Models   Entities
```

**Anti-patterns to watch for:**
- Business logic in controllers (fat controllers)
- Direct database calls from presentation layer
- Circular dependencies between layers

---

## Event-Driven Architecture

### Description
Components communicate through events. Producers emit events, consumers react asynchronously. Enables loose coupling and scalability.

### When to Use
- Systems with loose coupling requirements
- Async processing of workflows
- Multiple consumers need same data
- Audit trail/event sourcing required
- High throughput, eventual consistency acceptable
- Cross-service communication in microservices

### When NOT to Use
- Simple CRUD applications
- Strong consistency requirements (banking transactions)
- Synchronous request-response needed
- Team unfamiliar with event patterns
- Debugging/tracing complexity is a concern

### Key Components
- **Event Producers**: Emit events when state changes
- **Event Bus/Broker**: Kafka, RabbitMQ, SNS, Redis Pub/Sub
- **Event Consumers**: Subscribe and react to events
- **Event Store**: Persistent log (if event sourcing)

### Detection Heuristics
**Signs it's in use:**
- Message queue dependencies (Kafka, RabbitMQ, SQS)
- Pub/sub patterns, event handlers
- `on()`, `emit()`, `publish()`, `subscribe()` patterns
- Event classes/types with timestamps and metadata

**Anti-patterns:**
- "Event-driven" but actually request-reply
- Synchronous waits for event completion
- Missing dead-letter queues
- No event schema versioning

---

## Microservices Architecture

### Description
Application as collection of loosely coupled services. Each service is independently deployable, owns its data, and communicates via APIs.

### When to Use
- Large teams working on different features
- Independent scaling requirements per feature
- Polyglot technology requirements
- Continuous deployment per service needed
- Clear domain boundaries exist

### When NOT to Use
- Small teams (< 10 developers)
- Startup MVP phase
- Tightly coupled data requirements
- Limited DevOps capability
- When you can't define clear service boundaries

### Key Components
- **API Gateway**: Entry point, routing, authentication
- **Service Mesh**: Inter-service communication (Istio, Linkerd)
- **Service Registry**: Service discovery (Consul, Eureka)
- **Circuit Breaker**: Failure handling (Hystrix pattern)
- **Config Server**: Centralized configuration

### Detection Heuristics
**Signs it's in use:**
- Multiple repositories or service directories
- Docker/Kubernetes configurations
- API gateway configuration
- Service-to-service HTTP/gRPC calls
- Separate databases per service

**Anti-patterns (Distributed Monolith):**
- Services must deploy together
- Shared database across services
- Synchronous call chains
- Tight coupling via shared libraries

---

## CQRS (Command Query Responsibility Segregation)

### Description
Separates read and write operations into different models. Commands modify state, queries read state. Often combined with Event Sourcing.

### When to Use
- Read/write ratio heavily skewed (reads >> writes)
- Different optimization needs for reads vs writes
- Complex domain with audit requirements
- Event Sourcing is beneficial
- Separate scaling for read/write workloads

### When NOT to Use
- Simple CRUD applications
- Real-time consistency required
- Simple domain without complex queries
- Small scale with no scaling concerns

### Key Components
- **Command Handlers**: Process write operations
- **Query Handlers**: Process read operations
- **Write Model**: Normalized for consistency
- **Read Model**: Denormalized for query performance
- **Event Store**: (if combined with Event Sourcing)

### Detection Heuristics
**Signs it's in use:**
- Separate read/write paths in code
- Different database schemas for reads vs writes
- `CommandHandler`, `QueryHandler` classes
- Eventual consistency patterns
- Projection or read model rebuilding

---

## Hexagonal Architecture (Ports & Adapters)

### Description
Domain logic at center, surrounded by ports (interfaces) and adapters (implementations). Also known as Clean Architecture when combined with dependency inversion.

### When to Use
- Need to swap infrastructure easily (database, APIs)
- Strong testability requirements
- Long-lived application with changing requirements
- Multiple entry points (API, CLI, queues)
- Domain complexity warrants isolation

### When NOT to Use
- Simple scripts or utilities
- Throw-away prototypes
- Very simple domains
- When indirection overhead isn't justified

### Key Components
- **Domain Core**: Pure business logic, no external dependencies
- **Ports**: Interfaces defining domain boundaries
- **Adapters**: Implementations of ports (REST, DB, messaging)
- **Application Services**: Orchestrate use cases

### Detection Heuristics
**Signs it's in use:**
- `ports/`, `adapters/`, `domain/`, `application/` directories
- Interfaces in domain, implementations in adapters
- Dependency injection configuration
- Domain entities with no framework imports

**Directory patterns:**
```
src/
  domain/          # Pure business logic
  application/     # Use cases, ports (interfaces)
  infrastructure/  # Adapters (DB, HTTP, messaging)
  interfaces/      # API controllers, CLI
```

---

## Saga Pattern

### Description
Manages distributed transactions across services using a sequence of local transactions with compensating actions for rollback.

### When to Use
- Long-running business transactions across services
- Eventual consistency is acceptable
- Need to maintain data consistency without 2PC
- Complex workflows with multiple steps

### When NOT to Use
- Single service transactions
- Strong consistency required
- Simple operations without compensation needs

### Key Components
- **Saga Orchestrator**: Coordinates transaction steps (orchestration)
- **Event Choreography**: Services react to events (choreography)
- **Compensating Transactions**: Undo actions on failure
- **Saga Log**: Track transaction state

### Detection Heuristics
**Signs it's in use:**
- Workflow/saga classes with step definitions
- Compensating action handlers
- Transaction state tracking
- Step retry and timeout logic

---

## API Gateway Pattern

### Description
Single entry point for all client requests. Handles cross-cutting concerns like authentication, rate limiting, request routing.

### When to Use
- Multiple backend services
- Need consistent authentication/authorization
- Rate limiting and throttling required
- Request aggregation beneficial
- Protocol translation needed

### When NOT to Use
- Single backend service
- Internal service-to-service only
- When gateway becomes bottleneck

### Key Components
- **Route Configuration**: URL to service mapping
- **Authentication**: JWT validation, OAuth
- **Rate Limiter**: Request throttling
- **Load Balancer**: Traffic distribution
- **Cache Layer**: Response caching

### Detection Heuristics
**Signs it's in use:**
- Kong, AWS API Gateway, Nginx Plus configs
- Route configuration files
- Middleware chains for auth/rate-limiting
- Request transformation logic

---

## Circuit Breaker Pattern

### Description
Prevents cascading failures by failing fast when a service is unhealthy. Three states: Closed (normal), Open (failing fast), Half-Open (testing recovery).

### When to Use
- Calling external services that may fail
- Need to prevent cascade failures
- Want graceful degradation
- Service dependencies may timeout

### When NOT to Use
- Calls that must succeed (no fallback possible)
- Internal, same-process calls
- Database transactions (use retry instead)

### Key Components
- **Failure Threshold**: Count before opening
- **Timeout**: Time before trying half-open
- **Half-Open Tests**: Limited requests to test recovery
- **Fallback**: Alternative behavior when open

### Detection Heuristics
**Signs it's in use:**
- Hystrix, Resilience4j, Polly dependencies
- Circuit breaker configuration
- Fallback methods
- Health check endpoints
- State tracking (closed/open/half-open)

---

## Strangler Fig Pattern

### Description
Gradually replace legacy system by routing traffic to new implementation while keeping legacy running. Named after strangler fig tree.

### When to Use
- Migrating from monolith to microservices
- Incremental modernization needed
- Can't do big-bang replacement
- Need to maintain operations during migration

### When NOT to Use
- Complete rewrite is feasible
- Legacy system has no clear boundaries
- No routing layer available

### Key Components
- **Router/Facade**: Directs traffic to old or new
- **New Implementation**: Modern replacement
- **Legacy System**: Original system being replaced
- **Anti-Corruption Layer**: Translates between systems

### Detection Heuristics
**Signs it's in use:**
- Feature flags routing to old/new paths
- Adapter classes translating between systems
- Gradual deprecation of legacy endpoints
- Parallel deployment of old and new

---

## Backend for Frontend (BFF)

### Description
Dedicated backend per frontend type (web, mobile, IoT). Each BFF tailored to specific frontend needs.

### When to Use
- Multiple client types with different needs
- Mobile vs web have different data requirements
- Want to optimize payloads per client
- Frontend teams want API control

### When NOT to Use
- Single frontend type
- All clients have identical needs
- Small team (overhead not justified)

### Key Components
- **Web BFF**: Optimized for browser
- **Mobile BFF**: Optimized for mobile bandwidth
- **Backend Services**: Shared business logic
- **API Aggregation**: Combine multiple service calls

### Detection Heuristics
**Signs it's in use:**
- Multiple API projects: `api-web`, `api-mobile`
- Client-specific response shapes
- GraphQL with client-specific resolvers
- Separate deployment per frontend type

---

## Sidecar Pattern

### Description
Deploy auxiliary components alongside main application as separate process. Handles cross-cutting concerns without polluting main app.

### When to Use
- Need to add functionality without modifying app
- Cross-cutting concerns (logging, monitoring, proxy)
- Polyglot environment
- Kubernetes deployments

### When NOT to Use
- Simple applications
- Tight latency requirements
- Resource-constrained environments

### Key Components
- **Main Container**: Primary application
- **Sidecar Container**: Auxiliary functionality
- **Shared Storage**: Volume for communication
- **Network Proxy**: Inter-pod communication

### Detection Heuristics
**Signs it's in use:**
- Kubernetes pod with multiple containers
- Envoy, Istio proxy containers
- Logging/monitoring sidecars
- Shared volumes between containers

---

## Quick Reference Table

| Pattern | Scale | Complexity | When Primary | Key Signal |
|---------|-------|------------|--------------|------------|
| Layered | Small-Medium | Low-Medium | Clear separation | `controllers/services/repos` |
| Event-Driven | Medium-Large | High | Loose coupling | Message queues, pub/sub |
| Microservices | Large | High | Team scaling | Multiple repos, API gateway |
| CQRS | Medium-Large | High | Read-heavy | Separate read/write models |
| Hexagonal | Any | Medium | Testability | Ports, adapters, domain core |
| Saga | Large | High | Distributed TX | Compensating transactions |
| Circuit Breaker | Any | Low | External calls | Hystrix, fallbacks |
| API Gateway | Medium-Large | Medium | Multi-service | Route configs, Kong/Nginx |
| Strangler | Any | Medium | Migration | Feature flags, dual paths |
| BFF | Medium-Large | Medium | Multi-client | Separate APIs per client |
| Sidecar | Any | Medium | Cross-cutting | Multi-container pods |
