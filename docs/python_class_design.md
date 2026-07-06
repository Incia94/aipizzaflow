# Python Class Design Specification
## PizzaFlow AI

**Stage:** Python Class Design
**Status:** Approved
**Next Stage:** Traceability Matrix → Folder Structure

---

## Document Purpose

This document defines every Python class in the system — its type, its responsibilities, and the methods it owns. It is the bridge between the Services Specification and the Implementation. No code is written here. No Python syntax appears. Only class names, types, and responsibilities.

**Class types used in this document:**

| Type | Technology | Purpose |
|---|---|---|
| Entity | SQLAlchemy model | Persists a domain entity to the database |
| Request Schema | Pydantic model | Defines the shape of an API request; validates input |
| Response Schema | Pydantic model | Defines the shape of an API response; defines output |
| Repository Interface | Python interface | Defines the data access contract for a bounded context |
| Service | Plain Python class | Implements a business capability |
| Data Class | Pydantic model | Structures computed data (not persisted) |
| Exception | Python Exception | Represents a named error category |

---

## 1. Reference Context — Menu

### Entities

**`MenuItem`** (Entity)
Persists a pizza available for ordering.
- Fields: id, name, category, available_bases, available_toppings, price, is_available
- Loaded from CSV at startup. Read-only during operation.

---

### Repository Interface

**`MenuRepository`** (Repository Interface)
- `get_available_items() -> List[MenuItem]` — retrieves all MenuItem records where is_available is True
- `get_by_id(item_id) -> Optional[MenuItem]` — retrieves a specific MenuItem by ID; used by OrderService for availability and price validation

---

### Response Schemas

**`MenuItemResponse`** (Response Schema)
API response shape for a single menu item.
- Fields: id, name, category, available_bases, available_toppings, price

**`MenuResponse`** (Response Schema)
API response for the Retrieve Menu operation.
- Fields: items (list of MenuItemResponse)

---

### Service

**`MenuLoader`** (Service)
- `load_menu() -> MenuResponse` — returns all available menu items; the primary API-facing method corresponding to the Retrieve Menu operation

Note: Seeding the database from the menu CSV file at application startup is an initialization concern, not a public service operation.

---

## 2. Order Context

### Entities

**`Customer`** (Entity)
Persists a customer who placed an order.
- Fields: id, name, phone_number, created_at

**`Order`** (Entity)
Persists a confirmed customer purchase.
- Fields: id, customer_id, status (pending / paid), created_at, updated_at

**`OrderItem`** (Entity)
Persists one line item within an Order.
- Fields: id, order_id, menu_item_id, base_selected, toppings_selected, quantity, unit_price

Note: `unit_price` is captured from the MenuItem at the time the order is submitted, not referenced from the current MenuItem price.

---

### Repository Interface

**`OrderRepository`** (Repository Interface)
- `find_customer_by_phone(phone_number) -> Optional[Customer]` — identifies a returning customer
- `save_customer(customer_data) -> Customer` — persists a new customer record
- `save_order(customer_id) -> Order` — creates and persists a new Pending order
- `save_order_items(order_id, items) -> List[OrderItem]` — persists all line items for the order

---

### Request Schemas

**`CustomerRequest`** (Request Schema)
Request shape for customer details.
- Fields: name (required), phone_number (required)

**`OrderItemRequest`** (Request Schema)
Request shape for a single item in an order submission.
- Fields: menu_item_id (required), base_selected (required), toppings_selected (list), quantity (required, ≥ 1)

**`SubmitOrderRequest`** (Request Schema)
API request shape for the Submit Order operation.
- Fields: customer (CustomerRequest), items (list of OrderItemRequest, min 1)

---

### Response Schemas

**`OrderItemResponse`** (Response Schema)
Response shape for a single order item.
- Fields: menu_item_id, name, base_selected, toppings_selected, quantity, unit_price

**`PendingOrderResponse`** (Response Schema)
API response shape for a successfully submitted order.
- Fields: order_id, status, customer (name, phone_number), items (list of OrderItemResponse), created_at

---

### Service

**`OrderService`** (Service)
- `submit_order(customer_data: CustomerRequest, items: List[OrderItemRequest]) -> PendingOrderResponse` — validates all business rules, creates Customer (or identifies returning customer), creates Order with status Pending, creates all OrderItems with unit prices captured from current menu. Returns the Pending Order Response.

---

## 3. Checkout Context

### Entities

**`Bill`** (Entity)
Persists the legal financial record of a transaction.
- Fields: id, order_id, subtotal, gst_rate, gst_amount, total_amount, created_at

**`Payment`** (Entity)
Persists the payment confirmation for a transaction.
- Fields: id, order_id, bill_id, payment_method, amount_paid, created_at

---

### Repository Interface

**`CheckoutRepository`** (Repository Interface)
- `get_pending_order(order_id) -> Optional[Order]` — retrieves a Pending order by ID for transaction validation
- `mark_order_paid(order_id) -> Order` — transitions the order status to Paid
- `save_bill(bill_data) -> Bill` — persists the bill record
- `save_payment(payment_data) -> Payment` — persists the payment record

---

### Request Schemas

**`CompleteCheckoutRequest`** (Request Schema)
API request shape for the Complete Checkout operation.
- Fields: pending_order_id (required), payment_method (required, one of: cash / card / upi)

---

### Response Schemas

**`BillResponse`** (Response Schema)
Response shape for bill details within a completed transaction.
- Fields: subtotal, gst_rate, gst_amount, total_amount

**`CompleteCheckoutResponse`** (Response Schema)
API response shape for a successfully completed checkout.
- Fields: order_id, status (paid), bill (BillResponse), payment_method, paid_at

---

### Service

**`CheckoutService`** (Service)
- `complete_checkout(pending_order_id, payment_method) -> CompleteCheckoutResponse` — performs all steps of the Checkout workflow atomically: validates the transaction, calculates the bill (subtotal + 18% GST), records payment, transitions order to Paid. All three writes (Order → Paid, Bill created, Payment created) occur in a single database transaction.

---

## 4. Analytics Context

### Data Classes

The Business Intelligence Model is structured as a hierarchy of Pydantic data classes. None of these are persisted — they are computed on demand by AnalyticsService.

**`RevenueMetrics`** (Data Class)
- total_revenue, net_revenue, gst_collected, discount_total
- revenue_by_day, revenue_by_week, revenue_by_month, revenue_by_hour
- revenue_by_pizza, revenue_by_payment_method

**`SalesMetrics`** (Data Class)
- total_orders, orders_by_hour, orders_by_day
- average_order_value, average_items_per_order
- largest_order, smallest_order

**`CustomerMetrics`** (Data Class)
- total_customers, new_customers, returning_customers
- repeat_purchase_rate, average_spend, visit_frequency
- customer_lifetime_value, days_since_last_visit
- retention_rate, churn_rate

**`ProductMetrics`** (Data Class)
- best_selling_pizza, worst_selling_pizza
- revenue_by_pizza, quantity_sold_by_pizza, pizza_ranking
- most_popular_topping, least_popular_topping
- most_common_combination, upsell_rate

**`PaymentMetrics`** (Data Class)
- cash_percentage, card_percentage, upi_percentage
- average_transaction_amount

**`GrowthMetrics`** (Data Class)
- revenue_growth, order_growth, customer_growth
- period_comparison (week-over-week, month-over-month)

**`BusinessIntelligenceModel`** (Data Class)
The top-level container. Single source of truth for all BI consumers.
- Fields: revenue (RevenueMetrics), sales (SalesMetrics), customers (CustomerMetrics), products (ProductMetrics), payments (PaymentMetrics), growth (GrowthMetrics), generated_at, filters_applied

---

### Repository Interface

**`AnalyticsRepository`** (Repository Interface)
Read-only access across all transactional entities.
- `get_paid_orders(filters) -> List[Order]` — retrieves all Paid orders matching the applied filters
- `get_order_items(order_ids) -> List[OrderItem]` — retrieves all line items for the given orders
- `get_bills(order_ids) -> List[Bill]` — retrieves all bill records for the given orders
- `get_customers(customer_ids) -> List[Customer]` — retrieves customer records for the given orders

---

### Request Schemas

**`AnalyticsRequest`** (Request Schema)
API request shape for the Retrieve Analytics operation.
- Fields: date_from (optional), date_to (optional), pizza_id (optional), customer_id (optional), payment_method (optional), category (optional)

---

### Response Schemas

**`AnalyticsResponse`** (Response Schema)
API response shape. Wraps the full BusinessIntelligenceModel.
- Fields: data (BusinessIntelligenceModel), generated_at

---

### Service

**`AnalyticsService`** (Service)
- `retrieve_business_intelligence(filters: AnalyticsRequest) -> BusinessIntelligenceModel` — retrieves all Paid transactions, applies the requested filters, aggregates by the analytical dimensions, calculates all deterministic metrics across all six business categories, and returns the complete Business Intelligence Model.

---

## 5. AI Advisor Context

### Request Schemas

**`AIQueryRequest`** (Request Schema)
API request shape for the Query AI Advisor operation.
- Fields: question (required, non-empty string)

---

### Response Schemas

**`AIQueryResponse`** (Response Schema)
API response shape.
- Fields: response (natural language string), generated_at

---

### Service

**`AIService`** (Service)
- `query(question: str) -> AIQueryResponse` — requests the full Business Intelligence Model from AnalyticsService, assembles a structured prompt combining the BI data and the user's question, calls the OpenRouter API, and returns the natural language response.

Note: The AI Advisor Context has no repository. It is stateless and accesses data exclusively through AnalyticsService.

---

## 6. Shared — Cross-Cutting

These classes belong to no single bounded context. They are implemented once and used system-wide.

### Exceptions

Five exception classes, mapping directly to the five error categories defined in the API Design:

**`InvalidInputError`** — Request does not conform to the expected contract.
**`BusinessRuleViolationError`** — Request is valid in shape but violates a business rule.
**`ResourceNotFoundError`** — Referenced resource does not exist.
**`ExternalServiceError`** — An external dependency (OpenRouter, database) failed.
**`UnexpectedSystemError`** — Unhandled internal error.

FastAPI exception handlers map each exception class to the appropriate HTTP response.

### Config

**`Settings`** (class, loaded from .env at startup)
- database_url
- openrouter_api_key
- openrouter_model
- menu_file_path

---

## Class Summary

| Context | Entities | Repository Interfaces | Request Schemas | Response Schemas | Services | Data Classes | Exceptions |
|---|---|---|---|---|---|---|---|
| Reference (Menu) | MenuItem | MenuRepository | — | MenuItemResponse, MenuResponse | MenuLoader | — | — |
| Order | Customer, Order, OrderItem | OrderRepository | CustomerRequest, OrderItemRequest, SubmitOrderRequest | OrderItemResponse, PendingOrderResponse | OrderService | — | — |
| Checkout | Bill, Payment | CheckoutRepository | CompleteCheckoutRequest | BillResponse, CompleteCheckoutResponse | CheckoutService | — | — |
| Analytics | — | AnalyticsRepository | AnalyticsRequest | AnalyticsResponse | AnalyticsService | RevenueMetrics, SalesMetrics, CustomerMetrics, ProductMetrics, PaymentMetrics, GrowthMetrics, BusinessIntelligenceModel | — |
| AI Advisor | — | — | AIQueryRequest | AIQueryResponse | AIService | — | — |
| Shared | — | — | — | — | — | Settings | InvalidInputError, BusinessRuleViolationError, ResourceNotFoundError, ExternalServiceError, UnexpectedSystemError |

**Total: 6 entities · 4 repository interfaces · 6 request schemas · 8 response schemas · 5 services · 7 data classes · 5 exceptions · 1 config**

---

## Traceability Chain

```
Bounded Context
      ↓
Service
      ↓
Public Method
      ↓
API Operation
```

| Bounded Context | Service | Public Method | API Operation |
|---|---|---|---|
| Reference (Menu) | MenuLoader | `load_menu()` | Retrieve Menu |
| Order | OrderService | `submit_order()` | Submit Order |
| Checkout | CheckoutService | `complete_checkout()` | Complete Checkout |
| Analytics | AnalyticsService | `retrieve_business_intelligence()` | Retrieve Analytics |
| AI Advisor | AIService | `query()` | Query AI Advisor |

---

*Approved. Next: Traceability Matrix → Folder Structure → Implementation.*
