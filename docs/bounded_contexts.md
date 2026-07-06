# Bounded Contexts Specification
## PizzaFlow AI

**Stage:** Bounded Contexts
**Status:** Approved
**Next Stage:** Services

---

## Document Purpose

This document identifies the independent business contexts within PizzaFlow AI. Each context represents a cohesive business capability with clear ownership of its domain entities, business rules, and transformations. It defines who owns what and how contexts communicate through business events.

This document does not discuss APIs, databases, services, Python classes, or folder structures.

---

## Context Map

```
┌──────────────────────────────────┐
│   Reference Context (Menu)       │
│   owns: MenuItem                 │
└──────────────────────────────────┘
          │                   │
     MenuItem             MenuItem
    (available)            (prices)
          │                   │
          ▼                   ▼
┌──────────────────┐   ┌────────────────────┐
│  Order Context   │   │  Checkout Context  │
│  owns: Order,    │──►│  owns: Bill,       │
│  OrderItem,      │   │  Payment           │
│  Customer        │   └────────────────────┘
└──────────────────┘             │
  publishes:                     │ Transaction Completed
  Order Confirmed                │
                                 ▼
                      ┌────────────────────┐
                      │ Analytics Context  │
                      │ owns: Business     │
                      │ Intelligence Model │
                      └────────────────────┘
                                 │
                                 │ Business Intelligence
                                 ▼
                      ┌────────────────────┐
                      │ AI Advisor Context │
                      │ owns: nothing      │
                      │ (stateless)        │
                      └────────────────────┘
```

---

## Event Flow

```
Customer confirms order
        │
        ▼
Order Confirmed
        │
        ▼
Checkout completes payment
        │
        ▼
Transaction Completed
        │
        ▼
Analytics computes Business Intelligence
        │
        ▼
Business Intelligence Ready
        │
        ▼
Rajan asks a business question
        │
        ▼
AI Response Generated
```

---

## 1. Reference Context — Menu

**Purpose:** Provide read-only menu data to the rest of the system.

**Note:** The Menu is a Reference Context, not a full bounded context. It has no independent business workflow, no decisions, and no transformations. It loads external data and makes it available to consuming contexts.

**Responsibilities:**
- Load the menu from an external file.
- Make menu items available to Order Context for browsing and selection.
- Make current menu prices available to Checkout Context for bill generation and price validation.
- Enforce menu availability rules.

**Inputs:**
- External menu file (CSV/Excel).

**Outputs:**
- Available menu items with names, customization options, and prices.

**Business Rules Owned:**
- Only menu items present in the loaded menu can be ordered.
- Unavailable menu items cannot be added to an order.
- The menu is read-only. It cannot be modified through the application.

**Domain Entities Owned:**
- `MenuItem`

**Events Published:**
- Menu Available

**Events Consumed:**
- None.

**External Dependencies:**
- External menu file (CSV/Excel).

---

## 2. Order Context

**Purpose:** Transform customer intent into a confirmed, frozen order.

**Responsibilities:**
- Capture customer details.
- Present available menu items to the customer.
- Allow item selection, customization, and quantity specification.
- Enforce interactive validation continuously throughout order building.
- Allow the customer to review and confirm the order.
- Transition the order to Pending state upon confirmation.

**Inputs:**
- Menu Available *(from Reference Context — Menu)*
- Customer input (name, phone number, pizza selections, customizations, quantities)

**Outputs:**
- Order Confirmed *(a frozen, valid Pending order ready for Checkout)*

**Business Rules Owned:**
- Customer Name is required.
- Phone Number is required.
- An order must contain at least one item before it can be confirmed.
- Every pizza must satisfy all menu customization requirements before it can be added to an order.
- Quantity per item must be ≥ 1.
- Once confirmed, an order cannot be modified.
- Order cancellation is not supported in this version.

**Domain Entities Owned:**
- `Order` *(from creation through confirmation)*
- `OrderItem`
- `Customer`

**Events Published:**
- Order Confirmed

**Events Consumed:**
- Menu Available *(from Reference Context — Menu)*

**External Dependencies:**
- None.

---

## 3. Checkout Context

**Purpose:** Transform a confirmed order into a completed business transaction.

**Responsibilities:**
- Perform Transaction Validation on the confirmed order.
- Generate the bill.
- Present the bill to the customer.
- Accept payment.
- Transition the order from Pending to Paid.
- Finalize the business transaction.

**Inputs:**
- Order Confirmed *(from Order Context)*
- Current menu prices *(from Reference Context — Menu, for price validation)*
- Customer payment

**Outputs:**
- Transaction Completed *(a Paid transaction available to downstream contexts)*

**Business Rules Owned:**
- Transaction Validation rules (see Business Rules Specification §7).
- GST of 18% is applied to every order.
- Discounts are not applicable in this version.
- Accepted payment methods: Cash, Card, UPI.
- Payment must be completed before the transaction is finalized.
- If payment fails, the order remains Pending. The customer may retry payment.
- A bill is generated once per order.

**Domain Entities Owned:**
- `Bill`
- `Payment`
- `Order` *(state transition only: Pending → Paid)*

**Events Published:**
- Transaction Completed

**Events Consumed:**
- Order Confirmed *(from Order Context)*

**External Dependencies:**
- None. *(Payment is recorded by method. No external payment gateway in this version.)*

---

## 4. Analytics Context

**Purpose:** Transform completed business transactions into objective Business Intelligence.

**Responsibilities:**
- Consume business events that carry transactional data.
- Apply user-selected filters.
- Aggregate data across business dimensions.
- Perform all deterministic business calculations.
- Produce the Business Intelligence Model.

**Note:** Analytics currently consumes only the Transaction Completed event because that is the only business event produced by PizzaFlow. As the system grows, Analytics may consume additional events (Customer Registered, Promotion Applied, etc.) without any change to its fundamental responsibility.

**Inputs:**
- Transaction Completed *(from Checkout Context)*
- Filter parameters (date range, pizza, customer, payment method, category)

**Outputs:**
- Business Intelligence Model *(the single source of truth for all BI consumers)*

**Business Rules Owned:**
- Only Paid transactions participate in Business Analytics.
- Analytics operates only on persisted transactions.
- Analytics produces deterministic, objective outputs.
- Analytics never performs interpretation or recommendation.

**Domain Entities Owned:**
- Business Intelligence Model

**Business Categories Owned:**
- Revenue Performance
- Sales Performance
- Customer Behaviour
- Product Performance
- Payment Analysis
- Business Growth

**Events Published:**
- Business Intelligence Ready

**Events Consumed:**
- Transaction Completed *(from Checkout Context)*

**External Dependencies:**
- None.

---

## 5. AI Advisor Context

**Purpose:** Transform Business Intelligence into business reasoning, interpretation, and recommendations.

**Responsibilities:**
- Accept a natural language business question from Rajan.
- Identify the Business Intelligence required to answer the question.
- Request relevant Business Intelligence from Analytics Context.
- Apply reasoning to patterns and relationships within that intelligence.
- Return a natural language response.

**Inputs:**
- Rajan's natural language question.
- Business Intelligence Model *(requested from Analytics Context)*

**Outputs:**
- Natural language response (explanation, recommendation, or answer).

**Business Rules Owned:**
- The AI Advisor reasons only over Business Intelligence. It never accesses transactional data directly.
- The AI Advisor never performs deterministic calculations.
- The AI Advisor provides recommendations only. Final decisions remain with the restaurant owner.
- The AI Advisor is purely reactive. It responds only when asked.

**Domain Entities Owned:**
- None. The AI Advisor context is stateless. It owns no data.

**Events Published:**
- AI Response Generated

**Events Consumed:**
- Business Intelligence Ready *(from Analytics Context)*

**External Dependencies:**
- OpenRouter API *(external LLM provider)*

---

## Context Relationships

| Upstream | Downstream | Ownership |
|---|---|---|
| Reference Context (Menu) | Order Context | Menu owns `MenuItem`. Order reads `MenuItem` for display and selection. |
| Reference Context (Menu) | Checkout Context | Menu owns `MenuItem` prices. Checkout reads prices for bill generation and price validation. |
| Order Context | Checkout Context | Order publishes `Order Confirmed`. Checkout owns transaction completion. |
| Checkout Context | Analytics Context | Checkout publishes `Transaction Completed`. Analytics owns Business Intelligence computation. |
| Analytics Context | AI Advisor Context | Analytics owns the Business Intelligence Model. AI Advisor requests it; Analytics provides it. |

---

## Architectural Principles Established

The following principles were established during this stage.

1. **A bounded context should own exactly one business transformation.**
   If a context creates orders, calculates revenue, and talks to AI, it owns too much. Every context in PizzaFlow transforms one input into one output:

   | Context | Input | Output |
   |---|---|---|
   | Menu | External file | Available menu data |
   | Order | Customer intent | Confirmed order |
   | Checkout | Confirmed order | Completed transaction |
   | Analytics | Completed transactions | Business Intelligence |
   | AI Advisor | Business Intelligence + Question | Business recommendation |

2. **Ownership, not access, defines a bounded context.**
   Multiple contexts may read the same data. Only one context may own it.

---

## Glossary

| Term | Meaning |
|---|---|
| Bounded Context | An independent business capability with clear ownership of its domain model, business rules, and transformation. |
| Reference Context | A context that holds read-only reference data. It has no business workflow or transformation of its own. |
| Context Map | A diagram showing the relationships and ownership boundaries between bounded contexts. |
| Domain Entity | A business object with a distinct identity, owned by exactly one context. |
| Business Event | A significant business occurrence that one context publishes and another may consume. |
| Upstream Context | A context whose output is consumed by a downstream context. |
| Downstream Context | A context that depends on the output of an upstream context. |
| Business Intelligence Model | The structured output of Analytics Context. The single source of truth for all BI consumers. |
| Order Confirmed | The business event that freezes an order and passes it to Checkout Context. |
| Transaction Completed | The business event that marks an order as Paid and makes the transaction available to Analytics Context. |

---

*This document is the approved specification for the Bounded Contexts stage. The next stage is Services.*
