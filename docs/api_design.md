# API Design Specification
## PizzaFlow AI

**Stage:** API Design
**Status:** Approved
**Next Stage:** Database Design

---

## Document Purpose

This document defines the contract between the frontend and the backend. It specifies what the API exposes, what each operation accepts as input, what it returns as output, and how errors are communicated. It does not define URL paths, HTTP methods, JSON schemas, or implementation details. Those belong to the implementation stage.

---

## 1. API Philosophy

> The API exposes business capabilities, not database tables or implementation details.

The five operations defined in this document correspond directly to the five bounded contexts in the Services Specification. There is no CRUD surface. The API does not expose raw entities for the frontend to assemble into business logic. Every operation represents a complete business capability delivered by a specific bounded context.

---

## 2. API Consumers

| Consumer | Frontend Page | Capabilities Consumed |
|---|---|---|
| Restaurant Operations UI | Place Order, Bill | Retrieve Menu, Submit Order, Complete Checkout |
| Business Intelligence UI | Dashboard | Retrieve Analytics |
| AI Advisor UI | AI Advisor | Query AI Advisor |

The Home page does not consume the API directly.

---

## 3. Resource Model

Five resources. Each maps to a bounded context.

| Resource | Owned By | Nature |
|---|---|---|
| Menu | Reference Context | Read-only reference data |
| Order | Order Context | Operational — created per customer transaction |
| Checkout | Checkout Context | Operational — finalizes a transaction |
| Analytics | Analytics Context | Intelligence — computed from completed transactions |
| AI Query | AI Advisor Context | Reasoning — responds to natural language questions |

---

## 4. Request / Response Contracts

---

### Menu

**Retrieve Menu**

*Input:* None.

*Output:* The complete list of available menu items. Each item includes its name, available base options, available topping options, and its price.

---

### Order

**Submit Order**

*Input:*
- Customer: name, phone number.
- Order Items: one or more items, each specifying the menu item, selected base, selected toppings, and quantity.

*Output:*
- Pending Order: a Pending Order ID, the submitted items with their confirmed prices, the customer details, and status = Pending.

---

### Checkout

**Complete Checkout**

*Input:*
- Pending Order ID identifying the Pending order to be finalised.
- Payment method: Cash, Card, or UPI.

*Output:*
- Completed transaction: bill summary (subtotal, GST amount, final payable amount), payment method recorded, and order status = Paid.

---

### Analytics

**Retrieve Analytics**

*Input:*
- Optional filter parameters: date range, pizza, customer, payment method, category.

*Output:*
- Business Intelligence Model: structured metrics across all six business categories (Revenue Performance, Sales Performance, Customer Behaviour, Product Performance, Payment Analysis, Business Growth).

*Note: If the Business Intelligence Model grows large, Analytics may expose partial models for specific business categories. This is a performance optimisation — it does not change the architectural boundary.*

---

### AI Query

**Query AI Advisor**

*Input:*
- A natural language business question from Rajan.

*Output:*
- A natural language response containing explanation, interpretation, or recommendation. The response is derived from the Business Intelligence Model, not from raw transactional data.

---

## 5. API Operations

### Restaurant Operations

| Operation | Resource | Triggered By |
|---|---|---|
| Retrieve Menu | Menu | Customer opens Place Order page |
| Submit Order | Order | Customer confirms the order |
| Complete Checkout | Checkout | Customer selects payment method and pays |

### Business Intelligence

| Operation | Resource | Triggered By |
|---|---|---|
| Retrieve Analytics | Analytics | Rajan opens the Dashboard |
| Query AI Advisor | AI Query | Rajan submits a question |

**Total: 5 operations.**

The API is intentionally minimal. Every operation traces back to a business capability defined in the Services Specification.

**Workflow State Note:** The Pending Order returned by Submit Order is treated as workflow state. The frontend retains this state (Pending Order ID, order items, bill details) until Checkout completes. The Bill page is a continuation of the same workflow — not a new data retrieval. No GET /orders operation is required during an active Checkout workflow. If a user refreshes mid-workflow, local state is lost and the workflow restarts. This is an acceptable constraint for the MVP.

---

## 5a. Operation Ownership

Every API operation maps to exactly one bounded context. No operation crosses a context boundary.

```
Restaurant Operations UI
        │
        ├── Retrieve Menu      →  Reference Context
        │
        ├── Submit Order       →  Order Context
        │
        └── Complete Checkout  →  Checkout Context

Business Intelligence UI
        │
        └── Retrieve Analytics →  Analytics Context

AI Advisor UI
        │
        └── Query AI Advisor   →  AI Advisor Context
```

---

## 6. Validation Strategy

Validation occurs at two distinct layers with distinct responsibilities.

| Layer | Validation Type | Responsibility | Owned By |
|---|---|---|---|
| API Layer | Input Validation | Ensures the request is structurally correct: required fields are present, data types are valid, values are within acceptable format. | API Layer |
| Service Layer | Business Validation | Ensures the request satisfies all business rules. Applied by the responsible bounded context. | Checkout Context (Transaction Validation), Order Context (Interactive Validation) |

**The API layer never enforces business rules.** Business rules remain inside the bounded contexts.

If input validation fails, the error is returned immediately without the request reaching the service layer.

---

## 7. Error Model

Errors are categorised by cause. HTTP status codes are assigned during implementation.

| Category | Meaning | Example |
|---|---|---|
| **Invalid Input** | The request does not conform to the expected contract. Required field missing, wrong type, or unrecognised value. | Submitting an order with no customer name. |
| **Business Rule Violation** | The request is structurally valid but violates a business rule. | Attempting to checkout an empty order. Item no longer available at time of checkout. |
| **Resource Not Found** | The referenced resource does not exist. | Checkout request with a Pending Order ID that does not exist. |
| **External Service Failure** | An external dependency failed. | OpenRouter API unavailable when an AI query is made. |
| **Unexpected System Error** | An unhandled internal error. Indicates a defect, not a business condition. | Unexpected database error. |

Every error response communicates: the error category, a human-readable message, and (where applicable) which field or resource caused the error.

---

## 8. API Principles

| Principle | Application |
|---|---|
| Expose business capabilities, not database entities | Five operations corresponding to five bounded contexts. No generic CRUD surface. |
| Every API operation maps to exactly one bounded context | See Operation Ownership (§5a). No operation crosses a context boundary. |
| The API layer contains no business logic | Input validation only. All business rules enforced in the Service Layer. |
| Backend produces data. Frontend presents data. | Every response is a structured data object. The API makes no presentation decisions. |
| The AI Advisor never receives raw transactions | The AI Query operation returns reasoning derived from Business Intelligence only. |
| Each stage refines the previous stage, never redefines it | Every operation here corresponds to a capability already defined in the Services and Bounded Contexts Specifications. |

---

## 9. Out of Scope

The following are explicitly excluded from this API and should not be assumed as oversights.

- Authentication and authorisation
- API versioning
- Pagination
- Bulk operations
- WebSockets or real-time updates
- Streaming responses
- GraphQL
- Rate limiting
- Menu management endpoints (menu is loaded server-side from a file, not via the API)
- File upload endpoints

---

*This document is the approved specification for the API Design stage. The next stage is Database Design.*
