# Security — the never-list (always applies)

The model is `docs/reference/security-privacy.md`; the one-page rules are the invariants in
`docs/implementation/01-conventions.md`.

- **Never log or print** passwords, tokens, session or CSRF values, cookies, `Authorization` headers,
  provider codes, request bodies, query strings, emails, or any medical, legal-internal, identity or
  finance field — in logs, traces, error responses, test output or screenshots.
- **Never take a tenant from the request.** It comes from the verified session, a job, or an audited
  platform operation.
- **Never let a role or tenant membership alone grant confidential data;** never bypass a policy for an
  administrator; `SUPER_ADMIN` holds no tenant data.
- **Never commit a secret**, a real personal record, or a real organisation's data. Fixtures and seeds
  are synthetic, on `.test` domains. A secret that reaches the tree is rotated first, removed second.
- **Never weaken a guard** — no `--no-verify`, no disabled rule, no skipped test, no loosened ruleset —
  and never add coding-assistant attribution to a commit, title or PR body.
- **Never invent** a legal, medical, compliance or provider fact. An unanswered question is an OPEN item
  with a safe default in the master plan.
