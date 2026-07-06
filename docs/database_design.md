# Database Design Specification
## PizzaFlow AI

**Stage:** Database Design
**Status:** Approved
**Next Stage:** Consistency Review → Folder Structure

---

## Document Purpose

This document defines what business information PizzaFlow AI must persist, why it must be persisted, who owns it, and how entities relate. It does not define SQL schemas, column types, indexes, or ORM models. Those belong to the implementation stage.

---

## 1. Database Philosophy

> The database persists business facts — information whose value outlasts the process that produced it and cannot be recovered if lost.

This immediately excludes:
- Intermediate computation results
- Derived aggregations
- AI-generated responses
- Application session state

Everything in the database must be a record of something that actually happened in the business.

---

## 2. Persistence Model

### What deserves to be persisted?

The test is: **if the system restarted tomorrow, what business information would be irrecoverably lost?**

| Information | Persist? | Reason |
|---|---|---|
| Customer identity | ✅ | Required to associate orders with customers. Cannot be reconstructed if lost. |
| Menu items | ✅ | Reference data required for order validation and analytics. Loaded from file but stored for stability. |
| Orders | ✅ | The central business fact. Every downstream capability depends on it. |
| Order items | ✅ | Records exactly what was purchased — which pizzas, bases, toppings, quantities, and prices at time of order. |
| Bill | ✅ | Legal financial record. Captures the exact GST rate and total at the moment of the transaction. See §3. |
| Payment | ✅ | Confirms financial fulfilment. Records how and when the customer paid. |
| Business Intelligence Model | ❌ | Always recomputable from persisted transactions. Storing it would create a derivable copy that can go stale. |
| Analytics aggregations | ❌ | Derivable. Recomputed on demand by AnalyticsService. |
| AI responses | ❌ | Generated on demand. No long-term business value in storing them. |

---

## 3. Persistent Entities

---

### Customer

**Purpose:** Records the identity of a person who placed an order. Enables customer tracking, repeat purchase identification, and customer analytics.

**Lifetime:** Created when a customer submits their first order. Exists indefinitely as a historical record.

**Owner:** Order Context.

---

### MenuItem

**Purpose:** Reference data defining available pizzas — their names, customisation options (bases, toppings), and prices. Provides a stable, queryable reference for OrderItems and validation.

**Lifetime:** Loaded from the external menu file at application startup. Updated by reloading the file. Does not change during a customer session.

**Owner:** Reference Context.

---

### Order

**Purpose:** The central business fact. Represents a confirmed purchase by a customer. All business intelligence — revenue, sales, customer analytics — is derived from persisted Orders.

**Lifetime:** Created as Pending when the customer submits the order. Transitions to Paid when Checkout is completed. Exists indefinitely as an immutable historical record thereafter.

**Lifecycle Ownership:** Ownership of the Order follows its lifecycle. At every moment there is exactly one owning context.

| Lifecycle Stage | Owning Context |
|---|---|
| Building (pre-confirmation) | Order Context |
| Pending | Checkout Context |
| Paid | Checkout Context |
| Historical Record | Checkout Context |

Ownership transfers to Checkout Context at the moment the customer confirms the order. Order Context can no longer modify it thereafter.

---

### OrderItem

**Purpose:** Records the individual line items within an Order — which menu item was selected, which base and toppings were chosen, the quantity, and the unit price at the time of ordering.

**Why unit price is captured at order time:** Menu prices may change after an order is placed. Storing the price at order time ensures historical accuracy for analytics and prevents billing discrepancies.

**Lifetime:** Created together with the Order. Immutable after the Order is confirmed.

**Owner:** Order Context.

---

### Bill

**Purpose:** The legal financial record of the transaction. Captures the subtotal, the GST rate applied, the GST amount, any discount applied, and the total payable amount — all as they were at the exact moment the Bill was issued.

**Why Bill is persisted despite being calculable:**
The Bill could theoretically be recomputed from OrderItems and the current GST rule. However, the GST rate is a business rule subject to change. If the rate changes from 18% to a different value, recomputing historical bills would produce legally incorrect figures. The Bill is therefore a **legal business fact** — an immutable record of the financial terms as agreed at the moment of the transaction — not a derivable calculation.

**Lifetime:** Created during Checkout after Transaction Validation passes. Immutable.

**Owner:** Checkout Context.

---

### Payment

**Purpose:** Confirms that the financial obligation for an Order has been fulfilled. Records the payment method chosen, the amount paid, and when payment was made.

**Lifetime:** Created when payment is processed. Immutable.

**Owner:** Checkout Context.

---

## 4. Entity Ownership

| Entity | Owned By | Write Access |
|---|---|---|
| Customer | Order Context | Created by Order Context |
| MenuItem | Reference Context | Loaded at startup; read-only during operation |
| Order | Order Context → Checkout Context | Lifecycle ownership. Order Context creates; ownership transfers to Checkout Context at confirmation. |
| OrderItem | Order Context | Created by Order Context; immutable thereafter |
| Bill | Checkout Context | Created by Checkout Context; immutable thereafter |
| Payment | Checkout Context | Created by Checkout Context; immutable thereafter |

**Rule:** Only the owning context writes to its entities. Analytics Context and AI Advisor Context read only — they never write.

---

## 5. Relationships

```
Customer
    │
    │ one customer places many orders
    │
    ▼
Order ──────────────────────── OrderItem
    │                               │
    │ one order has                 │ each item references
    │ one bill and one payment      │ one menu item
    ▼                               ▼
   Bill                         MenuItem
   Payment
```

**Relationship summary:**

| From | To | Cardinality |
|---|---|---|
| Customer | Order | One customer → many Orders |
| Order | OrderItem | One Order → many OrderItems |
| OrderItem | MenuItem | Many OrderItems → one MenuItem |
| Order | Bill | One Order → one Bill |
| Order | Payment | One Order → one Payment |

---

## 6. Transaction Boundaries

A transaction boundary defines a set of writes that must succeed or fail atomically. No partial state is acceptable.

### Checkout Completion

When a customer completes checkout, the following three writes must occur as a single atomic transaction:

1. Order status updated → Paid
2. Bill created for the Order
3. Payment created for the Order

**If any one of these fails, all three must be rolled back.** An Order marked Paid with no Bill, or a Payment recorded against an Order still showing Pending, represents an invalid business state.

### Order Submission

When a customer submits an order, the following writes must occur atomically:

1. Customer created or identified
2. Order created with status Pending
3. All OrderItems created for the Order

---

## 7. Read Model

Defines which contexts read which data, and through what path.

| Consumer | Data Read | Access Path |
|---|---|---|
| Order Context | MenuItem (for display and validation) | Directly via Reference Context |
| Checkout Context | Order, OrderItems, MenuItem prices (for bill calculation) | Directly |
| Analytics Context | Order, OrderItem, Bill, Payment, Customer | Read-only queries via AnalyticsService |
| AI Advisor Context | Business Intelligence Model | Via AnalyticsService only — never reads raw tables |
| Frontend (all pages) | All data | Via API only — never directly |

**Rule:** Analytics Context is the only context authorised to read the full transaction history for reporting purposes. No other context aggregates historical data across all Orders.

**Rule:** The AI Advisor Context never reads raw database tables. It consumes the Business Intelligence Model produced by AnalyticsService.

---

## 8. Database Principles

| Principle | Application |
|---|---|
| Persist business facts, not derivable information | Business Intelligence metrics, analytics aggregations, and AI responses are not stored |
| Validate once, trust thereafter | Data is validated before write (Checkout Transaction Validation). Analytics reads trusted Paid records without re-validating. |
| Ownership determines write access | Each entity is written only by its owning context. Analytics and AI never write. |
| Backend owns persistence | The frontend never reads from or writes to the database directly. All persistence flows through the Service Layer. |
| Unit prices are captured at order time | Protects historical accuracy if menu prices change after an order is placed |
| Bill is a legal record, not a cache | Bill is persisted because it captures the exact tax rate at transaction time — a fact that cannot be safely recomputed if business rules change |

---

## 9. Out of Scope

The following are explicitly excluded from this database design and should not be assumed as oversights.

- Database replication or read replicas
- Sharding or horizontal partitioning
- Materialised views or pre-computed aggregations
- Data warehouse or analytical database (separate OLAP store)
- Event sourcing or event store
- CQRS (Command Query Responsibility Segregation)
- Soft deletes or archival strategy
- Audit logging table
- Full-text search indexes
- Time-series optimisation

---

*Draft only. Pending architecture review.*
