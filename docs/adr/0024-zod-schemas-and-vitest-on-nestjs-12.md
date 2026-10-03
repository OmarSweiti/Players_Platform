# ADR-0024 — On NestJS 12: Zod schemas for validation and the contract, Vitest for tests

**Status:** Accepted · 3 October 2026 · **Requirements:** SR-CORE-005, SR-API-003, SR-CORE-002,
TEST-001, TEST-002 · **Owners:** `0.2.3`, `0.2.9`, `0.3.2`, `0.3.9` · **Relates to:**
[ADR-0010](0010-api-contract.md), [ADR-0022](0022-the-sysrd-stack-kept-current.md)

## Context
`0.2.9` moves the backend to NestJS 12 (released 27 August 2026), which brings three changes that matter
here.
- **Validation.** Its route decorators accept a Standard Schema (`@Body({ schema })`, `@Query`,
  `@Param`). A `StandardSchemaValidationPipe` and a `StandardSchemaSerializerInterceptor` give
  schema-driven requests and responses. class-validator remains Nest's documented default.
- **The contract.** `@nestjs/swagger` 12 reflects those schemas into the OpenAPI document through a
  `standardSchemaConverter`.
- **Modules.** Nest's packages now ship as ES modules. On 28 September 2026, `@nestjs/testing` 12 failed
  under this repository's Jest setup with "Must use import to load ES Module". New ES-module Nest
  projects default to Vitest.

The web app already validates forms with Zod and runs Vitest. The plan had specified class-validator
DTOs and Jest, and none of that code is written yet: the test harness (`0.2.3`) and strict validation
(`0.3.2`) are both still ahead.

## Decision
1. **Request validation uses Zod 4 schemas** attached through NestJS 12's `schema` option.
   - Bodies use strict objects, so an unknown property is refused, just as `forbidNonWhitelisted` would
     refuse it.
   - Strings and arrays are bounded, path ids are UUIDs, and query parameters are coerced explicitly.
   - Failures map to `VALIDATION_FAILED` problem details with field errors (ADR-0010).
   - New code does not use class-validator.
2. **Response schemas** may be applied by the serializer interceptor as a second line of defence. They
   never replace the explicit field selection of the confidential projections (invariant I-2).
3. **The OpenAPI document is generated from the same schemas** by `@nestjs/swagger` 12. `0.3.9` chooses
   the converter (Zod 4's own `z.toJSONSchema` or `zod-openapi`). The document is OpenAPI 3.1 and is
   committed and diffed as ADR-0010 requires.
4. **The backend's tests run on Vitest**, which loads ES modules natively.
   - The `unit`, `integration` and `e2e` projects keep their disjoint globs.
   - Nest's dependency injection needs decorator metadata, which Vitest's default transform drops, so
     SWC compiles TypeScript in tests.
   - The harness of `0.2.3` is built on Vitest from the start, so `0.2.9` has no test runner to replace.
5. **Order:** strict validation (`0.3.2`) waits for the NestJS 12 upgrade (`0.2.9`), so validation is
   written once.

## Alternatives rejected
- **class-validator decorators.** They still work, but the API and the web app would then validate in
  two different languages, and the OpenAPI document would come from a third description, the Swagger
  CLI plugin's reading of the DTO classes.
- **Jest with ES-module support.** It is still experimental and is what failed on 28 September.
- **`nestjs-zod` on NestJS 11 first.** It means writing validation twice.

## Consequences
- One validation language across the product.
- Request validation and the contract come from one source, so they cannot drift apart.
- One test runner in both applications.
- The test catalog's names and globs are unchanged; only the runner differs. Verify commands become
  `npx vitest run …`.

## Revisit when
NestJS deprecates the Standard Schema path, or Zod stops implementing Standard Schema.
