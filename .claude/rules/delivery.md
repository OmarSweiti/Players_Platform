# Delivery — every pull request (always applies)

The flow is `docs/implementation/02-development-workflow.md` ("The microstep lifecycle") and
`docs/implementation/03-github-workflow.md` ("Review and approval").

1. **Validate before asking for review.** Start the stack (`just up`) and both applications from the
   branch; exercise every scenario the change touches through `https://sadara.localhost` — a screen in
   Arabic and English, an endpoint by real requests, one case that must fail. Capture screenshots
   (`cd frontend && npm run evidence -- --out <dir> <name>=<url>…`) and the requests with their answers;
   write the report: environment, then each scenario's steps, expected, seen, result.
2. **Open it, then post the evidence.** `just pr` opens the PR as the engineering app, assigned to the
   maintainer with their review requested. In the umbrella, `just evidence <PR URL> <report.md>
   <screenshots>` posts the evidence for the head commit; the `validation` check refuses a PR without it.
3. **Stop for the maintainer's approval.** Report the PR and wait. Never merge before they approve;
   never bypass a rule. A push after the approval dismisses it: validate again, ask again. Dependabot's
   PRs need their approval too.
4. **Merge with `just merge`** once approved and green; record in the umbrella by the same route.
5. **No sign of an assistant on GitHub.** Commits and branches are the maintainer's; no co-author
   trailer, no "Generated with", no assistant name — in a commit, branch, title, PR body, comment,
   screenshot or report.
6. **Evidence is synthetic.** Never a secret, token, cookie, password or personal value in a screenshot
   or a transcript: the security never-list applies to evidence too.
