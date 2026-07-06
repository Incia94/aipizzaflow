# Domain Model
## PizzaFlow AI

**Stage:** Domain Model
**Status:** Approved (refined through Database Design stage per Principle 16)
**Note:** This document was updated after Database Design to reflect two refinements: Bill was added as a domain entity, and Analytics was removed as a persistent entity (it produces a computed output, not a stored record).

---

## Document Purpose

This document defines the business entities that exist in the PizzaFlow AI domain, their meaning, and their relationships. It does not define database columns, class attributes, or implementation details. Those belong to later stages.

---

## Domain Entities

### Customer

A person who places an order at the restaurant. Identified by name and phone number. A customer may place multiple orders over time.

---

### MenuItem

A pizza available for ordering. Has a name, a set of available base options, a set of available topping options, and a price. Defined by the menu file. Read-only within the application.

---

### Order

The central business entity. Represents a confirmed purchase by a customer. All business intelligence is derived from Orders. An Order has a lifecycle: it begins as Pending when confirmed and becomes Paid when payment is processed.

---

### OrderItem

A single line within an Order. Records which MenuItem was selected, which base and toppings were chosen, the quantity, and the unit price at the time of ordering. An Order contains one or more OrderItems.

---

### Bill

The legal financial record of a transaction. Produced by Checkout after Transaction Validation. Records the subtotal, GST rate applied, GST amount, and total payable amount — all as they were at the exact moment the Bill was issued. Immutable after creation.

---

### Payment

Confirms that the financial obligation for an Order has been fulfilled. Records the payment method (Cash, Card, or UPI), the amount paid, and the timestamp. Immutable after creation.

---

## What Is Not a Domain Entity

### Business Intelligence Model

The Business Intelligence Model is a **computed output** produced by the Analytics Context on demand. It is derived deterministically from persisted Orders, OrderItems, Bills, and Payments. It is not a domain entity and is not persisted.

### Analytics

Analytics is a **bounded context** — it defines a business capability (converting transactions into Business Intelligence). It is not a domain entity. Earlier in the design process it was listed as an entity; this was a terminology imprecision resolved during the Database Design stage.

---

## Entity Relationships

```
Customer
    │
    │ places many
    ▼
Order ────────────────────── OrderItem
    │                              │
    │ has one                      │ references one
    ▼                              ▼
   Bill                        MenuItem
   Payment
```

| Relationship | Cardinality |
|---|---|
| Customer → Order | One customer places many Orders |
| Order → OrderItem | One Order contains many OrderItems |
| OrderItem → MenuItem | Many OrderItems reference one MenuItem |
| Order → Bill | One Order has one Bill |
| Order → Payment | One Order has one Payment |

---

## The Central Entity

**Order** is the central business entity. It is the fact from which all other records — Bill, Payment, OrderItems — originate. It is the primary input to Business Analytics. All business intelligence is ultimately derived from Orders.

---

*This document reflects the domain model as refined through the Functional Decomposition, Business Rules, Bounded Contexts, and Database Design stages.*
