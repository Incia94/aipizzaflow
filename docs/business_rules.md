# Business Rules Specification
## PizzaFlow AI

**Stage:** Business Rules
**Status:** Approved
**Next Stage:** Bounded Contexts

---

## Document Purpose

This document defines the business rules that govern all operations within PizzaFlow AI. These rules are deterministic, non-negotiable constraints that the system must enforce. They are independent of implementation — they apply regardless of which layer enforces them.

---

## 1. Customer Rules

| Rule | Constraint |
|---|---|
| Customer Name | Required. |
| Phone Number | Required. |

---

## 2. Menu Rules

- Only menu items present in the loaded menu can be ordered.
- Unavailable menu items cannot be added to an order.
- The menu is read-only within PizzaFlow AI. It is loaded from an external file and cannot be modified through the application.

---

## 3. Order Rules

| Rule | Constraint |
|---|---|
| Minimum Items | An order must contain at least one item before it can be confirmed. |
| Customization | Every pizza must satisfy all menu customization requirements before it can be added to an order. |
| Quantity | Quantity per item must be ≥ 1. |
| Confirmation | Once confirmed, an order cannot be modified. |
| Cancellation | Not supported in this version. |

---

## 4. Order State Rules

| Transition | Trigger | Condition |
|---|---|---|
| → Pending | Customer confirms order | Order contains at least one valid item |
| Pending → Paid | Payment processed successfully | Transaction validation passed |

No other states exist. The system does not track orders beyond Paid.

---

## 5. Billing Rules

- The bill shall accurately reflect the total payable amount for the order.
- The final payable amount shall include all applicable taxes and discounts.
- **GST:** 18%, applied to every order.
- **Discounts:** Not applicable in this version.
- A bill is generated once per order, during Checkout, after Transaction Validation passes.

---

## 6. Payment Rules

- Accepted payment methods: Cash, Card, UPI.
- Payment must be completed before the transaction is finalized.
- A successful payment transitions the order from Pending to Paid.
- If payment fails, the order remains Pending. The customer may retry payment.

---

## 7. Transaction Validation Rules

These rules are enforced during Checkout before a bill is generated or payment is accepted.

| Rule | Constraint |
|---|---|
| Non-empty Order | The order must contain at least one item. |
| Item Completeness | Every order item must satisfy all menu customization requirements and have a valid quantity. |
| Item Availability | All menu items in the order must still be available at time of checkout. |
| Price Validity | Prices must reflect current menu prices at time of checkout. |
| Payable Amount | The final payable amount must be calculable and greater than zero. |

---

## 8. Analytics Rules

- Only Paid transactions participate in Business Analytics.
- Business Analytics shall operate only on persisted transactions.
- Business Analytics shall produce deterministic, objective outputs.
- Business Analytics shall never perform interpretation or recommendation.

---

## 9. AI Rules

- The AI Advisor shall reason only over Business Intelligence produced by Business Analytics.
- The AI Advisor shall never perform deterministic calculations.
- The AI Advisor shall never access transactional data directly.
- The AI Advisor provides recommendations only.
- Final business decisions remain with the restaurant owner.

---

## Glossary

| Term | Meaning |
|---|---|
| Business Rule | A deterministic constraint that governs business operations. |
| Business Intelligence | Objective, deterministic metrics produced by Business Analytics. |
| Business Analytics | The system function that converts completed transactions into Business Intelligence. |
| Business Intelligence Model | The structured output of Business Analytics. The single source of truth for all BI consumers. |
| AI Restaurant Advisor | The system function that interprets Business Intelligence to provide recommendations. |
| Transaction Validation | Verification that a confirmed order satisfies all business rules before payment is accepted. |
| Pending | A confirmed order that is awaiting successful payment. |
| Paid | A successfully completed and persisted transaction. |

---

*This document is the approved specification for the Business Rules stage. The next stage is Bounded Contexts.*
