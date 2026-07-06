# Services Specification
## PizzaFlow AI

**Stage:** Services
**Status:** Approved
**Next Stage:** System Architecture

---

## Document Purpose

This document maps each bounded context's business capabilities to the software services that implement them. It defines what each service is responsible for at the business level, not at the implementation level.

This document does not discuss Python classes, method signatures, databases, APIs, or folder structures.

---

## Rule Applied

> A service exists only if it implements a business capability owned by its bounded context.

---

## How to Read This Document

Each bounded context is presented in two views:

**Business View** — the business capability as defined in the Bounded Contexts Specification.
**Software View** — the service that implements that capability and its responsibilities.

---

## 1. Reference Context — Menu

### Business View

- Load the menu from an external file.
- Make available menu items accessible to consuming contexts.
- Enforce menu availability and read-only rules.

### Software View

**`MenuLoader`**
- Load menu items from the external file.
- Make the loaded menu available for the duration of the application session.
- Check whether a menu item is currently available.

---

## 2. Order Context

### Business View

- Capture customer details.
- Present the available menu and allow item selection, customization, and quantity input.
- Enforce interactive validation continuously throughout order building.
- Confirm the order, freezing it and transitioning it to Pending.

### Software View

**`OrderService`**
- Create a new order for a customer.
- Add an item (with customization and quantity) to the order.
- Remove an item from the order.
- Enforce interactive validation on each item before it is added.
- Review the complete order.
- Confirm the order, transitioning it to Pending state.

---

## 3. Checkout Context

### Business View

- Perform Transaction Validation on the confirmed order.
- Calculate the bill.
- Accept payment by the customer's chosen method.
- Finalize the business transaction.

### Software View

**`CheckoutService`**
- Validate the confirmed order against all transaction validation rules.
- Calculate the subtotal, apply GST (18%), and produce the Bill.
- Accept and record the customer's payment (Cash, Card, or UPI).
- Finalize the transaction, transitioning the order to Paid.

---

## 4. Analytics Context

### Business View

- Retrieve completed (Paid) transactions.
- Apply user-selected filters across business dimensions.
- Aggregate and calculate deterministic metrics across all six business categories.
- Produce the Business Intelligence Model.

### Software View

**`AnalyticsService`**
- Retrieve Paid transactions.
- Apply filters: date range, pizza, customer, payment method, category.
- Aggregate data by the requested analytical dimensions.
- Calculate deterministic metrics for all six business categories:
  - Revenue Performance
  - Sales Performance
  - Customer Behaviour
  - Product Performance
  - Payment Analysis
  - Business Growth
- Produce and return the Business Intelligence Model.

*Note: As business complexity grows, AnalyticsService may internally decompose into sub-components per category (RevenueAnalytics, CustomerAnalytics, etc.). This is a refactoring decision within the Analytics Context, not an architectural change.*

---

## 5. AI Advisor Context

### Business View

- Accept a natural language business question from Rajan.
- Identify and request the relevant Business Intelligence.
- Apply reasoning over that intelligence.
- Return a natural language response.

### Software View

**`AIService`**
- Receive a natural language business question.
- Request the relevant Business Intelligence from AnalyticsService.
- Prepare context: assemble the Business Intelligence and question into a structured prompt. *(Internal step — not a separate service.)*
- Call the external OpenRouter API.
- Return the natural language response.

---

## Service Map

```
Reference Context (Menu)
└── MenuLoader

Order Context
└── OrderService

Checkout Context
└── CheckoutService

Analytics Context
└── AnalyticsService

AI Advisor Context
└── AIService
```

---

*This document is the approved specification for the Services stage. The next stage is System Architecture.*
