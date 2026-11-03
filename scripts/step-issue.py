#!/usr/bin/env python3
"""Open the issue of the microstep you are starting, and file it on the delivery board.

  python3 scripts/step-issue.py <N.N.N>             # open it in the umbrella; file it on the board
  python3 scripts/step-issue.py <N.N.N> --dry-run   # print it; open nothing
  python3 scripts/step-issue.py --self-test

One issue per microstep, in the umbrella, opened when the step starts
(docs/implementation/03-github-workflow.md, "The board"). It links to the step
rather than copying it: the phase file is the plan of record, and a copy
would drift. Each application PR for the step says `Part of
OmarSweiti/Players_Platform#<issue>`; the umbrella PR that records the step
done says `Closes #<issue>`, and the board moves the card to Done.

Refused: a step the plan does not define, one already done or superseded, one
with a dependency that is not done (02-development-workflow.md, "Pick"), and a
step that already has an issue, open or closed.
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UMBRELLA = "OmarSweiti/Players_Platform"
BLOB = "https://github.com/%s/blob/development/" % UMBRELLA

_spec = importlib.util.spec_from_file_location("check_plan", os.path.join(ROOT, "scripts", "check-plan.py"))
plan = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(plan)


class Refused(Exception):
    pass


def anchor(path, heading):
    """GitHub's anchor for a heading line, counting the repeats before it as GitHub does."""
    seen, fence = {}, False
    for line in plan.read(path).split("\n"):
        if line.startswith("```"):
            fence = not fence
            continue
        m = None if fence else re.match(r"^#{1,6}\s+(.*?)\s*#*\s*$", line)
        if m:
            found = plan.slug(m.group(1), seen)
            if line == heading:
                return found
    raise Refused("no heading %r in %s" % (heading, path))


def step_issue(root, sid, existing):
    """The issue for step `sid` as (title, body); `existing` is the umbrella's issues, as {title, url}."""
    findings = []
    steps = plan.load_plan(root, findings)
    rows = plan.load_progress(root, findings)
    step = steps.get(sid)
    if step is None:
        raise Refused("the plan defines no step %s" % sid)
    status = plan.status_of(rows, sid)
    if status in ("done", "superseded"):
        raise Refused("step %s is %s in progress.md" % (sid, status))
    open_deps = ["%s (%s)" % (d, plan.status_of(rows, d)) for d in step.deps if plan.status_of(rows, d) != "done"]
    if open_deps:
        raise Refused("step %s depends on %s: never start a step whose dependencies are open" % (sid, ", ".join(open_deps)))
    title = "%s — %s" % (sid, step.title)
    for issue in existing:
        if issue["title"].startswith(sid + " — "):
            raise Refused("step %s already has an issue: %s" % (sid, issue["url"]))
    path = os.path.join(root, step.path)
    block = plan.read(path).split("\n")[step.line - 1:]
    text = "\n".join(block[1:])
    text = re.split(r"\n#{2,3} ", "\n" + text)[0]
    done_when = " ".join(plan.field(text, "Done when").split())
    depends = plan.field(text, "Depends on") or "—"
    body = "\n".join([
        "**Step:** [`%s` — %s](%s%s#%s)" % (sid, step.title, BLOB, step.path, anchor(path, block[0])),
        "**Repo:** %s · **Size:** %s · **Depends on:** %s" % (" + ".join(step.repos), step.size, depends),
        "",
        "**Done when:** %s" % (done_when or "—"),
        "",
        "The step is the plan's, and the plan is the record; this issue tracks it in flight, on the delivery "
        "board. Each application PR for it says `Part of %s#<this issue>`; the umbrella PR that records it "
        "done says `Closes #<this issue>`." % UMBRELLA,
    ])
    return title, body


def gh(*args, stdin=None):
    result = subprocess.run(["gh"] + list(args), input=stdin, capture_output=True, text=True)
    if result.returncode != 0:
        raise Refused("gh %s: %s" % (" ".join(args[:2]), result.stderr.strip()))
    return result.stdout


def main(argv):
    if argv == ["--self-test"]:
        return self_test()
    if not argv or not re.match(r"^\d+\.\d+\.\d+[a-z]?$", argv[0]) or argv[1:] not in ([], ["--dry-run"]):
        print(__doc__.strip().split("\n\n")[1], file=sys.stderr)
        return 2
    sid, dry = argv[0], argv[1:] == ["--dry-run"]
    try:
        existing = json.loads(gh("issue", "list", "--repo", UMBRELLA, "--state", "all", "--limit", "1000",
                                 "--search", "%s in:title" % sid, "--json", "title,url"))
        title, body = step_issue(ROOT, sid, existing)
        if dry:
            print("%s\n\n%s" % (title, body))
            return 0
        maintainer = UMBRELLA.split("/")[0]
        url = gh("issue", "create", "--repo", UMBRELLA, "--title", title, "--assignee", maintainer,
                 "--body-file", "-", stdin=body).strip().splitlines()[-1]
    except Refused as why:
        print("step-issue: REFUSED — %s" % why, file=sys.stderr)
        return 1
    print("step-issue: %s" % url)
    if subprocess.run(["bash", os.path.join(ROOT, "scripts", "gh-project-item.sh"), url]).returncode != 0:
        print("step-issue: the issue is open, but its card is not filed: run just gh-project-item %s" % url, file=sys.stderr)
    number = url.rsplit("/", 1)[-1]
    print("step-issue: application PRs say `Part of %s#%s`; the umbrella PR that records the step done says `Closes #%s`"
          % (UMBRELLA, number, number))
    return 0


FIXTURE = {
    "docs/implementation/phase-0-fixture.md": """# Phase 0 — Fixture

## Group 0.1 — First

### 0.1.1 — The first step
**Repo:** backend · **Size:** S · **Depends on:** — · **Requirements:** —
**Tests:** `the_first_step_works`
**Done when:** the first thing is true.

### 0.1.2 — The second step: two repositories
**Repo:** backend + frontend · **Size:** M · **Depends on:** `0.1.1` · **Requirements:** —
**Tests:** `the_second_step_works`
**Verify:** `just check`
**Done when:** the second thing is true,
across two lines.

### 0.1.3 — The third step
**Repo:** umbrella · **Size:** S · **Depends on:** `0.1.2` · **Requirements:** —
**Done when:** later.

## Group 0.2 — Second

### 0.2.1 — A superseded step
**Repo:** umbrella · **Size:** S · **Depends on:** — · **Requirements:** —
""",
    "docs/implementation/progress.md": """| Step | Title | Repo | Status | Evidence |
|---|---|---|---|---|
| 0.1.1 | The first step | backend | done | https://github.com/OmarSweiti/Players_Platform_Backend/pull/1 |
| 0.1.2 | The second step: two repositories | backend + frontend | todo |  |
| 0.1.3 | The third step | umbrella | todo |  |
| 0.2.1 | A superseded step | umbrella | superseded |  |
""",
}


def self_test():
    failures = []
    tmp = tempfile.mkdtemp(prefix="step-issue-self-")
    try:
        for rel, text in FIXTURE.items():
            os.makedirs(os.path.dirname(os.path.join(tmp, rel)), exist_ok=True)
            plan.write(os.path.join(tmp, rel), text)

        def expect(label, sid, needles=(), refused=None, existing=()):
            try:
                title, body = step_issue(tmp, sid, list(existing))
                got = title + "\n" + body
                missing = [n for n in needles if n not in got]
                if refused or missing:
                    failures.append("%s: wanted %s, got %r" % (label, refused or missing, got))
                    return
            except Refused as why:
                if not refused or refused not in str(why):
                    failures.append("%s: wanted %s, refused: %s" % (label, needles or refused, why))
                    return
            print("  ok   %s" % label)

        print("the issue a microstep gets")
        expect("a ready step gets its title, a link to its heading and its Done when", "0.1.2", (
            "0.1.2 — The second step: two repositories\n",
            "(%sdocs/implementation/phase-0-fixture.md#012--the-second-step-two-repositories)" % BLOB,
            "**Repo:** backend + frontend · **Size:** M · **Depends on:** `0.1.1`",
            "**Done when:** the second thing is true, across two lines.",
            "Part of %s#<this issue>" % UMBRELLA,
        ))
        expect("a step already done is refused", "0.1.1", refused="is done")
        expect("a superseded step is refused", "0.2.1", refused="is superseded")
        expect("a step with an open dependency is refused", "0.1.3", refused="depends on 0.1.2 (todo)")
        expect("a step the plan does not define is refused", "0.9.9", refused="defines no step")
        expect("a step that has an issue is refused", "0.1.2", refused="already has an issue",
               existing=[{"title": "0.1.2 — The second step: two repositories", "url": "https://x/1"}])
        expect("another step's issue does not count", "0.1.2", ("0.1.2 — ",),
               existing=[{"title": "0.1.20 — Another", "url": "https://x/2"}])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for f in failures:
        print("  FAILED  " + f)
    print("step-issue: %s" % ("every case holds" if not failures else "%d failed" % len(failures)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
