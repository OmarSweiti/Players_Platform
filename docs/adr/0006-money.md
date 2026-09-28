# ADR-0006 — Money as NUMERIC(19,4) with currency rules

**Status:** Accepted · 28 September 2026 · **Requirements:** SR-CT-005, SR-TR-006 · **Owner:** `0.4.7` ·
**Negotiated:** Claude first proposed integer minor units and conceded

## Context
Money is `Decimal(…, 2)` today, but the agency's currency, the Jordanian dinar, has three decimals; an
enrollment payment has no currency; the requirements set no scale, rounding or settlement rule.

## Decision
`NUMERIC(19,4)` with a currency code; a global `CurrencyDefinition(code, minorUnitExponent, enabled)`
lists the approved currencies (JOD for certain — OPEN-09 for the rest). Payable amounts may not exceed
their currency's exponent; NaN, infinity and excess scale are refused before PostgreSQL could round them.
A `Money` type wraps the exact decimal and its currency; amounts travel as decimal strings
(`{ "amount": "1250.500", "currency": "JOD" }`); rounding is an explicit domain operation; currencies
never mix without a recorded rate.

## Alternatives rejected
- **Integer minor units (BigInt)** — equally exact, but it fights the existing Decimal schema and makes
  intermediate amounts (percentages, pro-rating) awkward. Serialisation was not the deciding argument:
  both travel as strings.
- **Floating point** — inexact.

## Consequences
One migration converts four columns; every money field is a `Money` in code and a string on the wire.

## Revisit when
Settlement or accounting (Phase 3 finance) needs a precision or rounding rule this does not express.
