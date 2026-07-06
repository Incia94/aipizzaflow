# Traceability Matrix
## PizzaFlow AI

**Stage:** Pre-Implementation Final Verification
**Status:** Approved
**Purpose:** Proof that every layer of the architecture is traceable from business intent to implementation artifact.

---

## Document Purpose

This matrix is the final pre-implementation artifact. It spans every layer of the architecture — from business capability to persistence — and verifies that nothing is unanchored.

Every row represents one complete, traceable pathway: from the business problem that justified it, through the architecture that structured it, to the implementation artifact that will realise it.

If a cell is empty, it is by explicit design decision, not by omission.

---

## Full Traceability Matrix

| Business Capability | Bounded Context | Service | Public Method | API Operation | Request Schema | Response Schema | Entities Written | Persistence |
|---|---|---|---|---|---|---|---|---|
| Browse Menu | Reference | MenuLoader | `load_menu()` | Retrieve Menu | — | MenuResponse | — | `menu_items` (read-only) |
| Build Order | Order | OrderService | `submit_order()` | Submit Order | SubmitOrderRequest | PendingOrderResponse | Customer, Order, OrderItem | `customers`, `orders`, `order_items` |
| Complete Checkout | Checkout | CheckoutService | `complete_checkout()` | Complete Checkout | CompleteCheckoutRequest | CompleteCheckoutResponse | Bill, Payment | `bills`, `payments` |
| Generate Business Intelligence | Analytics | AnalyticsService | `retrieve_business_intelligence()` | Retrieve Analytics | AnalyticsRequest | AnalyticsResponse | — | Not persisted — computed on demand |
| Answer Business Question | AI Advisor | AIService | `query()` | Query AI Advisor | AIQueryRequest | AIQueryResponse | — | Not persisted — stateless response |

---

## Context Data Access Summary

| Context | Write Access | Entities Written | Read Access | Entities Read |
|---|---|---|---|---|
| Reference | Startup only | MenuItem | Yes | MenuItem |
| Order | Yes | Customer, Order, OrderItem | Yes (via MenuRepository) | MenuItem |
| Checkout | Yes | Bill, Payment | Yes (via CheckoutRepository) | Order, OrderItem |
| Analytics | No | — | Yes — read-only, all transactional entities | Order, OrderItem, Bill, Customer |
| AI Advisor | No | — | No — accesses data exclusively via AnalyticsService | — |

---

## Repository Interface Summary

| Repository Interface | Owned By | Read / Write | Operations |
|---|---|---|---|
| MenuRepository | Reference Context | Read | `get_available_items()`, `get_by_id()` |
| OrderRepository | Order Context | Write | `find_customer_by_phone()`, `save_customer()`, `save_order()`, `save_order_items()` |
| CheckoutRepository | Checkout Context | Write | `get_pending_order()`, `mark_order_paid()`, `save_bill()`, `save_payment()` |
| AnalyticsRepository | Analytics Context | Read only | `get_paid_orders()`, `get_order_items()`, `get_bills()`, `get_customers()` |

The AI Advisor Context has no repository. It is stateless and receives all data through AnalyticsService.

---

## Validation Ownership

| Validation Type | Owned By | Mechanism | Responsibility |
|---|---|---|---|
| Input Validation | API Layer | Pydantic Request Schemas | Ensures the request is structurally correct |
| Interactive Validation | Order Context | OrderService | Ensures all customisations are valid at order time |
| Transaction Validation | Checkout Context | CheckoutService | Protects the atomicity and integrity of the payment transaction |

---

## Error Category Mapping

| Error Category | Exception Class | Example |
|---|---|---|
| Invalid Input | `InvalidInputError` | Order submitted with no customer name |
| Business Rule Violation | `BusinessRuleViolationError` | Checkout attempted with an already-paid Order ID |
| Resource Not Found | `ResourceNotFoundError` | Checkout with a non-existent Pending Order ID |
| External Service Failure | `ExternalServiceError` | OpenRouter API unavailable during an AI query |
| Unexpected System Error | `UnexpectedSystemError` | Unhandled database exception |

---

## Architecture Principle Spot-Check

The five principles most likely to require active attention during implementation, verified against this matrix.

| Principle | Verification |
|---|---|
| #5 — Backend produces data, frontend presents data | Every response is a structured schema. No presentation logic in Python. |
| #7 — Deterministic computation and AI reasoning are separate | AnalyticsService computes the BI Model. AIService receives it and reasons over it. |
| #10 — Service exists only for a business capability | Every service maps to exactly one API operation. Five services, five operations. |
| #15 — Unidirectional flow | Menu → Order → Checkout → Analytics → AI. No backwards calls exist in this matrix. |
| #19 — Lifecycle ownership transfers at confirmation | Order Context writes during build. Checkout Context takes ownership at completion. |

---

## Completeness Check

| Category | Count | Classes |
|---|---|---|
| Entities | 6 | MenuItem, Customer, Order, OrderItem, Bill, Payment |
| Repository Interfaces | 4 | MenuRepository, OrderRepository, CheckoutRepository, AnalyticsRepository |
| Request Schemas | 6 | SubmitOrderRequest, CustomerRequest, OrderItemRequest, CompleteCheckoutRequest, AnalyticsRequest, AIQueryRequest |
| Response Schemas | 8 | MenuItemResponse, MenuResponse, OrderItemResponse, PendingOrderResponse, BillResponse, CompleteCheckoutResponse, AnalyticsResponse, AIQueryResponse |
| Services | 5 | MenuLoader, OrderService, CheckoutService, AnalyticsService, AIService |
| Data Classes (BI) | 7 | RevenueMetrics, SalesMetrics, CustomerMetrics, ProductMetrics, PaymentMetrics, GrowthMetrics, BusinessIntelligenceModel |
| Exceptions | 5 | InvalidInputError, BusinessRuleViolationError, ResourceNotFoundError, ExternalServiceError, UnexpectedSystemError |
| Config | 1 | Settings |

---

*Architecture phase complete. This matrix is the final proof of traceability before Folder Structure and Implementation begin.*
