# Functional Decomposition Specification
## PizzaFlow AI

**Stage:** Functional Decomposition
**Status:** Approved
**Next Stage:** Bounded Contexts

---

## Document Purpose

This document defines the functional responsibilities of PizzaFlow AI.

It specifies what the system does from a business perspective, establishes clear boundaries between functional areas, and serves as the approved specification for the Bounded Contexts stage.

This document intentionally excludes implementation details such as services, APIs, databases, folder structures, programming languages, and frameworks.

---

## 1. Product Scope

PizzaFlow AI is a restaurant management system. It digitizes ordering, billing, payment, and business intelligence. It does not automate restaurant operations.

### In Scope

| Module | Function |
|---|---|
| Restaurant Operations | Order Management, Checkout |
| Business Intelligence | Business Analytics, AI Restaurant Advisor |

### Out of Scope

- Kitchen Operations
- Inventory Management
- Staff Scheduling
- Supplier Management
- Delivery Management
- Customer Management (as a product module)
- Menu Management (as a product module)

**Note:** `Customer` and `MenuItem` are domain entities. They support the operational workflow but do not have dedicated management modules in this version.

---

## 2. Order State Machine

```
Pending → Paid
```

| State | Definition |
|---|---|
| Pending | Customer has confirmed the order. The order is frozen and enters Checkout. |
| Paid | Payment has been processed. The transaction is persisted and available for Business Analytics. |

The system's responsibility ends at **Paid**. Kitchen preparation and fulfillment are outside the scope of this project.

---

## 3. Functional Decomposition

### 3.1 Order Management

**Purpose:** Enable a customer to build a complete, valid order.

**Activities:**

1. Capture customer details
2. Display menu
3. Select pizzas
4. Customize pizzas (base, toppings)
5. Specify quantities
6. Add items to order
7. Interactive validation *(continuous — prevents invalid input as the order is built)*
8. Review order
9. Confirm order *(order becomes Pending; no further modification permitted)*

**Boundary:** Order Management ends when the customer confirms the order. The order is frozen.

---

### 3.2 Checkout

**Purpose:** Convert a confirmed order into a completed business transaction.

**Activities:**

1. Business validation *(verifies the confirmed order satisfies all business rules before payment)*
2. Generate bill
3. Display bill
4. Customer selects payment method
5. Process payment
6. Mark order as Paid
7. Persist transaction

**Boundary:** Checkout ends when the transaction is persisted. Business Analytics and the AI Restaurant Advisor consume the transaction from this point onward.

---

### 3.3 Business Analytics

**Purpose:** Convert transactional data into objective business intelligence.

**Process:**

1. Retrieve completed transactions
2. Apply filters
3. Aggregate data
4. Perform deterministic calculations
5. Produce structured business intelligence

**Output:** A structured **Business Intelligence Model** containing objective, deterministic business metrics. This model serves as the single source of truth for all business intelligence consumers, including the frontend dashboards and the AI Restaurant Advisor. Business Analytics does not present, interpret, or recommend — it computes.

**Business Categories:**

| Category | Business Question |
|---|---|
| Revenue Performance | How much money is the business making? |
| Sales Performance | What is the restaurant selling? |
| Customer Behaviour | Who are the customers and how do they behave? |
| Product Performance | Which menu items are performing well? |
| Payment Analysis | How are customers paying? |
| Business Growth | Is the business improving over time? |

*Discounts, GST, and pricing are sub-topics within Revenue Performance, not standalone categories.*

**Analytical Dimensions:**

Every business category can be analyzed across the following dimensions:

- Time (hour, day, week, month, year, custom range)
- Pizza
- Customer
- Payment Method
- Category

---

### 3.4 AI Restaurant Advisor

**Purpose:** Interpret objective business intelligence in response to natural language business questions.

**Interaction model:** Purely reactive. The AI Advisor responds only when Rajan asks a question. It does not generate unsolicited briefings or scheduled reports.

**Inputs:** The AI Advisor consumes only the **Business Intelligence Model** produced by Business Analytics. It never consumes raw transactional data.

**Workflow:**

```
Rajan asks a business question
        │
        ▼
Understand intent
        │
        ▼
Identify required business intelligence
        │
        ▼
Retrieve relevant business intelligence
        │
        ▼
Analyze patterns and relationships
        │
        ▼
Apply business reasoning
        │
        ▼
Generate recommendations
        │
        ▼
Return natural language response
```

**Responsibilities:**

- Explain business trends
- Interpret patterns in business intelligence
- Identify opportunities and risks
- Generate recommendations
- Answer natural language business questions

**Boundaries:**

- The AI Advisor never performs calculations.
- The AI Advisor never accesses the database directly.
- The AI Advisor only reasons over pre-computed business intelligence produced by Business Analytics.
- The AI Advisor never makes decisions on behalf of the business — it recommends. Rajan decides.

---

## 4. Validation Model

Two distinct types of validation exist in the system. They serve different purposes and belong to different stages.

| Type | Stage | Purpose |
|---|---|---|
| Interactive Validation | Order Management | Prevents invalid input as the order is built. Protects the user. |
| Business Validation | Checkout | Verifies the completed order satisfies all business rules before payment. Protects the transaction. |

---

## 5. Architectural Principles Established

The following principles were established during this stage and apply to all subsequent design decisions.

1. **Data persistence is an implementation concern, not a business function.** Users perform business operations. The system persists the outcome automatically.

2. **Do not confuse business entities with product capabilities.** An entity existing in the domain model does not mean it requires a dedicated product module.

3. **A business state should exist only if the business derives value from tracking it.** States without analytical or operational purpose add complexity without value.

4. **Every stage should trust the contract of the previous stage.** Validate at the point of writing. Downstream consumers operate on trusted output.

5. **Backend produces data. Frontend presents data.** The backend is never responsible for rendering. Its responsibility ends when it has produced correct, structured output.

6. **Each business category answers one primary business question.** Related concepts belong inside the category they influence — not alongside it as separate categories.

7. **The AI retrieves only the minimum business intelligence required to answer the question.** Focused context produces focused answers.

8. **Validation is not a single activity.** It occurs at multiple stages for different purposes. Merging them produces a system that is both over-engineered in the wrong places and under-protected in others.

---

*This document is the approved specification for the Functional Decomposition stage. The next stage is Bounded Contexts.*
