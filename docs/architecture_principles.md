# Architecture Principles
## PizzaFlow AI

**Status:** Living Document — updated as new principles are established.

---

## Document Purpose

This document consolidates every architectural principle discovered during the design of PizzaFlow AI. These principles represent a coherent way of thinking about software — not rules invented for this project, but conclusions arrived at through first principles reasoning.

They apply beyond PizzaFlow. Any business application following this methodology can be evaluated against them.

---

## I. Domain & Business Principles

**1. Don't confuse business entities with product capabilities.**
A domain model answers "What information does the business care about?" A functional decomposition answers "What capabilities does the product provide?" These are different views of the same system. An entity existing in the domain does not mean it needs its own product module.

**2. A business state should exist only if the business derives value from tracking it.**
States without analytical or operational purpose add complexity without value. Before introducing a new state, ask: does any business process or report depend on it?

**3. Each business category answers one primary business question.**
Related concepts that help explain that question belong inside the category — not alongside it as separate categories. This prevents category sprawl.

**4. The question is not "what can we build?" — it is "what must we build to solve the problem?"**
Scope is determined by the problem being targeted, not by technical capability or domain completeness.

---

## II. System Architecture Principles

**5. Backend produces data. Frontend presents data.**
The backend's responsibility ends when it has produced correct, structured output. It is never responsible for rendering, formatting for display, or visualization. These are UI concerns.

**6. Data persistence is an implementation concern, not a business function.**
Users perform business operations. The system persists the outcome automatically. No user explicitly "saves data" — persistence is a side effect of every business transaction.

**7. Deterministic computation and AI reasoning are strictly separate concerns.**
Python calculates. AI interprets. Business metrics are computed deterministically before the LLM receives them. The LLM never calculates, never accesses raw data, and never performs business logic.

---

## III. Bounded Context Principles

**8. A bounded context owns exactly one business transformation.**
Every context takes one input and produces one output. If a context creates orders, calculates revenue, and talks to AI, it owns too much. One transformation per context.

**9. Ownership, not access, defines a bounded context.**
Multiple contexts may read the same data. Only one context may own and modify it.

---

## IV. Service Principles

**10. A service exists only if it implements a business capability owned by its bounded context.**
This prevents utility services, helper services, and catch-all classes from appearing prematurely. Every service must trace back to a capability defined in the Bounded Contexts Specification.

---

## V. Validation Principles

**11. Validation is not a single activity — it occurs at different stages for different purposes.**
Interactive validation protects the user (prevents invalid input during order building). Transaction validation protects the business (ensures only complete, rule-compliant orders proceed to payment). Merging them produces a system that is over-engineered in the wrong places and under-protected in the right ones.

**12. Validate once, trust thereafter.**
Each stage is responsible for the correctness of its own output. Downstream stages operate on that trusted output without re-validating it. Validating the same data twice implies the first validation is insufficient.

---

## VI. AI Principles

**13. The AI receives only the minimum business intelligence required to answer the question.**
Focused context produces focused answers. Sending the entire Business Intelligence Model for every query adds noise without adding value.

---

**14. Business Capability Test**
Before creating a service, apply three tests: (1) Does it own a business capability? (2) Can the business describe it independently? (3) Would it exist if we changed the implementation technology? If any answer is no, it is an internal implementation detail — not a service. Components such as prompt formatters, serializers, HTTP clients, and database adapters fail this test.

---

**15. Unidirectional Flow**
Information flows in one direction through the system. Downstream contexts consume upstream outputs. No context reaches backwards or creates cyclic dependencies. This keeps the architecture understandable as it grows — every component knows its place in the flow.

---

**19. Ownership follows lifecycle, not existence.**
An entity may move between bounded contexts during its lifetime, but at any moment only one bounded context owns the authority to modify it. At every lifecycle stage there is exactly one owner — never simultaneous ownership.

**18. Persist business facts, even if they originate from deterministic calculations, once they become part of the historical business record.**
If a value can always be deterministically recomputed from current rules, default to not storing it. However, if the value captures conditions that existed at a specific moment in time — such as a tax rate, a price, or a discount — it becomes part of the historical business record and must be persisted. Business Intelligence metrics, analytics aggregations, and AI responses are not historical records — they do not belong in the database.

**17. Every API operation maps to exactly one business capability owned by exactly one bounded context.**
If one API operation must call multiple bounded contexts directly, a context boundary has been drawn incorrectly. The operation ownership mapping should be one-to-one: one consumer, one operation, one context.

**16. Each stage should refine the previous stage, never redefine it.**
Every stage from API Design onwards is a more concrete expression of the same architecture — not a new design. If a later stage forces a fundamental architectural change, the correct action is to return to the earlier document and correct it, rather than patching around the inconsistency. This is why design precedes implementation.

---

*Principles are added as they are established. They are never removed unless superseded by a more precise formulation.*
