# Performance and Locks (3.2.6)

## About This Lesson

This lesson covers **performance characteristics and concurrency control** in relational databases, with a focus on PostgreSQL. At this stage of the course, schema management (migrations) is already in place, so we can safely discuss how databases behave under real load and parallel access.

The goal of this lesson is not to memorize SQL commands, but to develop **engineering intuition**:
- why queries become slow over time,
- how concurrent transactions interact,
- where bottlenecks and blocking appear in real systems,
- and how application code influences database behavior.

---

## Lesson Structure

The lesson is divided into five entities, each focusing on one critical aspect of performance and concurrency.

### 3.2.6.1 Indexes

Indexes are auxiliary data structures that accelerate data access patterns such as filtering, joining, and ordering.

Key ideas:
- indexes are created **for queries**, not for tables;
- column order in composite indexes matters;
- primary keys and unique constraints automatically create indexes;
- indexes improve read performance at the cost of write performance.

This entity builds intuition about when indexes help, when they are ignored by the planner, and when they can actively hurt performance in write-heavy systems.

---

### 3.2.6.2 Transaction Isolation Levels

Isolation levels define **what data a transaction can see** when other transactions are running concurrently.

Key ideas:
- isolation levels control visibility, not locking strategy;
- PostgreSQL guarantees absence of dirty reads;
- higher isolation increases correctness but reduces concurrency;
- `Read Committed` is the practical default for most applications;
- `Serializable` is a correctness tool, not a default setting.

This entity explains database anomalies (non-repeatable reads, phantom reads) and how isolation levels trade correctness for performance.

---

### 3.2.6.3 Locks — Coordinating Parallel Access

Locks are the mechanism that ensures **safe concurrent modification** of shared data.

Key ideas:
- row-level locks allow high concurrency;
- table-level locks are expensive and should be used deliberately;
- deadlocks are inevitable in concurrent systems;
- databases resolve deadlocks by aborting one transaction;
- application code must be prepared to retry failed transactions.

This entity focuses on understanding locks as a coordination tool, not as a problem to eliminate.

---

### 3.2.6.4 Query Optimization — Finding Bottlenecks

Query optimization is the process of identifying and eliminating unnecessary work.

Key ideas:
- most slow queries were once fast;
- optimization starts with understanding the execution plan;
- `EXPLAIN ANALYZE` is the primary diagnostic tool;
- indexes are not the first optimization step;
- reducing data volume and work often yields the biggest gains.

This entity trains a systematic approach to performance analysis instead of trial-and-error tuning.

---

### 3.2.6.5 Examples with Python

This entity connects database theory with application-level behavior.

Key ideas:
- transaction boundaries in Python define lock lifetimes;
- lost updates occur when read–compute–write is not synchronized;
- `SELECT ... FOR UPDATE` is a fundamental pattern for safe updates;
- long-running transactions amplify contention and blocking;
- retries are a normal part of working with concurrent databases.

Examples are intentionally minimal and focus on illustrating behavior rather than providing full application code.

---

## Key Takeaways

By the end of this lesson, you should understand:
- how PostgreSQL balances performance and correctness;
- why concurrency issues are architectural, not accidental;
- how database behavior emerges from query structure and transaction scope;
- why performance problems must be approached systematically.

This lesson establishes the foundation required to design **scalable, concurrent, and predictable** agent systems that interact with relational databases under real-world load.

