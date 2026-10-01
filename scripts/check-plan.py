#!/usr/bin/env python3
"""The plan checks itself: `just check`, `just plan`, and CI's `test` job.

    python3 scripts/check-plan.py              verify; exit 1 on any finding
    python3 scripts/check-plan.py --write      regenerate the generated blocks, then verify
    python3 scripts/check-plan.py --self-test  prove every check still refuses what it must

The phase files are the single source of the plan. Everything else is either
hand-written (and checked) or generated from them (and checked for staleness):

  docs/implementation/phase-*.md      microsteps: ### N.N.N — title, then **Repo:**,
                                      **Depends on:**, **Requirements:**, **Tests:** …
  docs/implementation/progress.md     one row per microstep: status + evidence (hand-set)
  docs/implementation/README.md       <!-- plan:frontier --> block        (generated)
  docs/reference/test-catalog.md      <!-- plan:catalog --> block         (generated)
  docs/reference/traceability.md      <!-- plan:trace --> block           (generated)
  docs/implementation/00-master-plan.md  <!-- plan:deferred --> rows    (hand-written)
  docs/implementation/demo-milestone.md  <!-- milestone:steps --> rows  (hand-written, in build order)
                                      and its <!-- plan:milestone --> block (generated)
  docs/requirements/README.md         SHA-256 table of the frozen sources (hand-written)

A microstep marked `done` must cite a merged PR, have every dependency done, and
have every test it names present — and not skipped — in the application it
changes, at the commit the umbrella pins. A milestone lists steps in build order:
each one's dependencies come earlier in the list or are already done. Standard
library only.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from collections import OrderedDict

STATUSES = ("todo", "in-progress", "blocked", "done", "superseded")
APPS = ("backend", "frontend")
STEP_RE = re.compile(r"^### (\d+)\.(\d+)\.(\d+)([a-z]?) — (.+?)\s*$")
ID_IN_TICKS = re.compile(r"`(\d+\.\d+\.\d+[a-z]?)`")
TEST_NAME = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+){2,}$")
PR_URL = re.compile(r"https://github\.com/OmarSweiti/Players_Platform(?:_Backend|_Frontend)?/pull/\d+")
REQ_ID = re.compile(
    r"\b(BR-(?:OBJ|RULE)-\d{2}|PRD-[A-Z]+-\d{3}|UX-\d{3}|SYS-[A-Z]+-\d{3}"
    r"|SR-NFR-[A-Z0-9]+-\d{3}|SR-[A-Z]+-\d{3}|TEST-\d{3})\b")
REQ_CITE = re.compile(
    r"\b((?:BR-(?:OBJ|RULE)|PRD-[A-Z]+|SYS-[A-Z]+|SR-NFR-[A-Z0-9]+|SR-[A-Z]+|UX|TEST)-)"
    r"(\d{2,3})((?:\.\.\d{2,3}|(?:/\d{2,3})+)?)")
SKIPPED = re.compile(r"\b(?:it|test)(?:\.\w+)*\.(?:skip|todo|only|fixme)\b|\bx(?:it|test|describe)\s*\(")
SKIPPED_SUITE = re.compile(r"\b(?:describe|suite)(?:\.\w+)*\.(?:skip|only|todo|fixme)\s*\(|\bxdescribe\s*\("
                           r"|\btest\.describe(?:\.\w+)*\.(?:skip|only|fixme)\s*\(")
COMMENT = re.compile(r"^\s*(?://|/?\*|#)")
JS_FILES = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs")
PY_SKIP = re.compile(r"^\s*@(?:unittest\.skip\w*|unittest\.expectedFailure|pytest\.mark\.(?:skip|skipif|xfail))")
REPO_OF = {"umbrella": "Players_Platform", "backend": "Players_Platform_Backend", "frontend": "Players_Platform_Frontend"}
PR_PARTS = re.compile(r"https://github\.com/OmarSweiti/(Players_Platform(?:_Backend|_Frontend)?)/pull/(\d+)")
TEST_PATHS = {"backend": ["src", "test"], "frontend": ["src", "app", "tests", "e2e"],
              "umbrella": ["scripts", ".githooks"]}
MILESTONE = "docs/implementation/demo-milestone.md"
MILESTONE_ROW = re.compile(r"^\|\s*([A-Z])\b[^|]*\|(.*)\|\s*$", re.M)  # | A — stage name | `0.2.3` · `0.1.5` |
WEIGHT = {"S": 4, "M": 8, "L": 16}  # the size ceilings, in hours (00-master-plan.md, Effort model)
LINK = re.compile(r"(?<!!)\[[^\]\n]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


class Step:
    def __init__(self, sid, title, phase, path, line):
        self.id, self.title, self.phase, self.path, self.line = sid, title, phase, path, line
        self.repos, self.deps, self.reqs, self.tests = [], [], [], []
        self.size = ""


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def write(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def id_key(sid):
    m = re.match(r"(\d+)\.(\d+)\.(\d+)([a-z]?)$", sid)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4))


def field(block, name):
    """The text of a **Name:** field, up to the next field on the same line or the next field line."""
    m = re.search(r"\*\*" + re.escape(name) + r":\*\*\s*(.*?)(?=\s·\s\*\*|\n\*\*|\n\n|\n###|\Z)", block, re.S)
    return m.group(1).strip() if m else ""


def expand(cite):
    """SR-ACL-002/006/007 and SR-CORE-001..009 → individual IDs."""
    out = []
    for prefix, first, rest in REQ_CITE.findall(cite):
        width = len(first)
        if rest.startswith(".."):
            last = rest[2:]
            out += [prefix + str(n).zfill(width) for n in range(int(first), int(last) + 1)]
        else:
            out += [prefix + first] + [prefix + n for n in rest.split("/")[1:]]
    return out


def load_plan(root, findings):
    steps = OrderedDict()
    impl = os.path.join(root, "docs", "implementation")
    files = sorted(f for f in os.listdir(impl) if re.match(r"phase-\d+-.*\.md$", f))
    if not files:
        findings.append("docs/implementation: no phase-N-*.md files")
    for name in files:
        rel = "docs/implementation/" + name
        phase = int(re.match(r"phase-(\d+)-", name).group(1))
        lines = read(os.path.join(impl, name)).split("\n")
        heads = [(i, STEP_RE.match(l)) for i, l in enumerate(lines) if STEP_RE.match(l)]
        for n, (i, m) in enumerate(heads):
            sid = "%s.%s.%s%s" % m.group(1, 2, 3, 4)
            if int(m.group(1)) != phase:
                findings.append("%s:%d: step %s lives in the phase-%d file" % (rel, i + 1, sid, phase))
            if sid in steps:
                findings.append("%s:%d: step %s is defined twice (first at %s:%d)"
                                % (rel, i + 1, sid, steps[sid].path, steps[sid].line))
                continue
            end = heads[n + 1][0] if n + 1 < len(heads) else len(lines)
            block = "\n".join(lines[i + 1:end])
            block = re.split(r"\n## ", block)[0]
            s = Step(sid, m.group(5), phase, rel, i + 1)
            repo = field(block, "Repo")
            s.repos = [r.strip() for r in re.split(r"\s*\+\s*", repo) if r.strip()]
            if not s.repos:
                findings.append("%s:%d: step %s has no **Repo:**" % (rel, i + 1, sid))
            for r in s.repos:
                if r not in APPS + ("umbrella",):
                    findings.append("%s:%d: step %s names an unknown repo '%s'" % (rel, i + 1, sid, r))
            s.size = field(block, "Size")
            if s.size not in WEIGHT:
                findings.append("%s:%d: step %s has no **Size:** of S, M or L" % (rel, i + 1, sid))
            s.deps = ID_IN_TICKS.findall(field(block, "Depends on"))
            s.reqs = expand(field(block, "Requirements"))
            tests = field(block, "Tests")
            for tok in re.findall(r"`([^`]+)`", tests):
                if TEST_NAME.match(tok):
                    s.tests.append(tok)
                else:
                    findings.append("%s:%d: step %s: '%s' on the Tests line is not a lower_snake test name"
                                    % (rel, i + 1, sid, tok))
            steps[sid] = s
    return steps


def load_progress(root, findings):
    rel = "docs/implementation/progress.md"
    path = os.path.join(root, rel)
    rows = OrderedDict()
    if not os.path.exists(path):
        findings.append(rel + ": missing (run: python3 scripts/check-plan.py --write)")
        return rows
    for i, line in enumerate(read(path).split("\n"), 1):
        m = re.match(r"^\|\s*(\d+\.\d+\.\d+[a-z]?)\s*\|(.*)\|\s*$", line)
        if not m:
            continue
        cells = [c.strip() for c in m.group(2).split("|")]
        if len(cells) != 4:
            findings.append("%s:%d: a row needs 5 cells: step | title | repo | status | evidence" % (rel, i))
            continue
        sid = m.group(1)
        if sid in rows:
            findings.append("%s:%d: step %s has two rows" % (rel, i, sid))
        rows[sid] = {"title": cells[0], "repo": cells[1], "status": cells[2], "evidence": cells[3], "line": i}
    return rows


def load_milestone(root, steps, rows, findings):
    """The demo milestone's steps as (id, stage), in build order; [] when the plan has no milestone."""
    path = os.path.join(root, MILESTONE)
    if not os.path.exists(path):
        return []
    m = re.search(r"<!-- milestone:steps:begin -->(.*?)<!-- milestone:steps:end -->", read(path), re.S)
    if not m:
        findings.append("%s: no <!-- milestone:steps:begin/end --> block" % MILESTONE)
        return []
    listed = [(sid, stage) for stage, cell in MILESTONE_ROW.findall(m.group(1)) for sid in ID_IN_TICKS.findall(cell)]
    if not listed:
        findings.append("%s: the milestone lists no step" % MILESTONE)
    position = {}
    for n, (sid, _) in enumerate(listed):
        if sid in position:
            findings.append("%s: step %s is listed twice" % (MILESTONE, sid))
        position.setdefault(sid, n)
        if sid not in steps:
            findings.append("%s: step %s does not exist" % (MILESTONE, sid))
        elif status_of(rows, sid) == "superseded":
            findings.append("%s: step %s is superseded; list its replacement" % (MILESTONE, sid))
    for sid, _ in listed:
        for d in steps[sid].deps if sid in steps else []:
            if status_of(rows, d) == "done":
                continue  # a finished dependency is satisfied wherever it is listed
            if d in position:
                if position[d] > position[sid]:
                    findings.append("%s: %s is listed before its dependency %s — the list is the build order"
                                    % (MILESTONE, sid, d))
            else:
                findings.append("%s: %s depends on %s, which is neither in the milestone nor done"
                                % (MILESTONE, sid, d))
    if listed and listed[-1][0] in steps:
        last = listed[-1][0]
        reach, stack = set(), [last]
        while stack:
            for d in steps[stack.pop()].deps:
                if d in steps and d not in reach:
                    reach.add(d)
                    stack.append(d)
        for sid, _ in listed[:-1]:
            if sid in steps and sid not in reach and status_of(rows, sid) != "done":
                findings.append("%s: the milestone's last step %s does not depend on %s — the last step accepts "
                                "the whole milestone" % (MILESTONE, last, sid))
    return listed


def defined_requirements(root):
    ids = OrderedDict()
    reqdir = os.path.join(root, "docs", "requirements")
    for name in sorted(os.listdir(reqdir)):
        if re.match(r"0\d_.*\.md$", name):
            for rid in REQ_ID.findall(read(os.path.join(reqdir, name))):
                ids.setdefault(rid, name)
    return ids


def block_rows(text, name):
    m = re.search(r"<!-- plan:%s:begin -->(.*?)<!-- plan:%s:end -->" % (name, name), text, re.S)
    return m.group(1) if m else None


def deferred_requirements(root):
    text = read(os.path.join(root, "docs", "implementation", "00-master-plan.md"))
    rows = block_rows(text, "deferred") or ""
    return {m.group(1): m.group(2).strip() for m in re.finditer(r"^\|\s*([A-Z][A-Z0-9-]+-\d{2,3})\s*\|(.*)$", rows, re.M)}


# ---------------------------------------------------------------------------- checks

def check_graph(steps, findings):
    for s in steps.values():
        for d in s.deps:
            if d not in steps:
                findings.append("%s:%d: step %s depends on %s, which does not exist" % (s.path, s.line, s.id, d))
            elif steps[d].phase > s.phase:
                findings.append("%s:%d: step %s depends on %s in a later phase" % (s.path, s.line, s.id, d))
            elif d == s.id:
                findings.append("%s:%d: step %s depends on itself" % (s.path, s.line, s.id))
    state = {}

    def visit(sid, trail):
        state[sid] = 1
        for d in steps[sid].deps:
            if d not in steps or d == sid:
                continue
            if state.get(d) == 1:
                cycle = trail[trail.index(d):] + [d] if d in trail else [sid, d]
                findings.append("dependency cycle: " + " → ".join(cycle))
            elif d not in state:
                visit(d, trail + [d])
        state[sid] = 2

    for sid in steps:
        if sid not in state:
            visit(sid, [sid])


def check_tests_unique(steps, findings):
    owner = {}
    for s in steps.values():
        for t in s.tests:
            if t in owner and owner[t] != s.id:
                findings.append("%s:%d: test %s is named by both %s and %s — a test has one owner"
                                % (s.path, s.line, t, owner[t], s.id))
            owner.setdefault(t, s.id)


def check_progress(steps, rows, findings):
    rel = "docs/implementation/progress.md"
    for sid, s in steps.items():
        if sid not in rows:
            findings.append("%s: no row for %s (run: python3 scripts/check-plan.py --write)" % (rel, sid))
    for sid, r in rows.items():
        where = "%s:%d" % (rel, r["line"])
        if sid not in steps:
            findings.append("%s: row %s names no microstep in the phase files" % (where, sid))
            continue
        st = r["status"]
        if st not in STATUSES:
            findings.append("%s: %s has status '%s' (allowed: %s)" % (where, sid, st, ", ".join(STATUSES)))
        if st == "done":
            if not PR_URL.search(r["evidence"]):
                findings.append("%s: %s is done but cites no merged PR URL" % (where, sid))
            else:
                cited = {repo for repo, _ in PR_PARTS.findall(r["evidence"])}
                for app in steps[sid].repos:
                    if REPO_OF.get(app) not in cited:
                        findings.append("%s: %s is done but cites no merged PR for %s" % (where, sid, app))
            for d in steps[sid].deps:
                if d in rows and rows[d]["status"] != "done":
                    findings.append("%s: %s is done but its dependency %s is %s" % (where, sid, d, rows[d]["status"]))
        if st == "blocked" and not r["evidence"]:
            findings.append("%s: %s is blocked but says by what" % (where, sid))


def check_requirements(steps, defined, deferred, findings):
    owned = set()
    for s in steps.values():
        for rid in s.reqs:
            owned.add(rid)
            if rid not in defined:
                findings.append("%s:%d: step %s cites %s, which no requirement document defines"
                                % (s.path, s.line, s.id, rid))
    for rid in deferred:
        if rid not in defined:
            findings.append("00-master-plan.md deferred table: %s is not a requirement ID" % rid)
        elif rid in owned:
            findings.append("00-master-plan.md deferred table: %s is owned by a microstep; remove the deferral" % rid)
    for rid, doc in defined.items():
        if rid not in owned and rid not in deferred:
            findings.append("requirement %s (%s) is owned by no microstep and not deferred" % (rid, doc))


def check_checksums(root, findings):
    reqdir = os.path.join(root, "docs", "requirements")
    readme = read(os.path.join(reqdir, "README.md"))
    pairs = re.findall(r"`((?:source/)?[\w.-]+\.(?:docx|md))`\s*\|\s*`([0-9a-f]{64})`", readme)
    if not pairs:
        findings.append("docs/requirements/README.md: no checksum table")
    for rel, digest in pairs:
        path = os.path.join(reqdir, rel)
        if not os.path.exists(path):
            findings.append("docs/requirements/%s: listed in the checksum table but missing" % rel)
            continue
        with open(path, "rb") as fh:
            actual = hashlib.sha256(fh.read()).hexdigest()
        if actual != digest:
            findings.append("docs/requirements/%s: checksum differs — the frozen baseline was edited" % rel)


def slug(heading, seen):
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    text = text.replace("`", "").replace("*", "").strip().lower()
    base = re.sub(r"[^\w\- ]", "", text, flags=re.U).replace(" ", "-")
    n = seen.get(base, 0)
    seen[base] = n + 1
    return base if n == 0 else "%s-%d" % (base, n)


def anchors(path, cache):
    if path not in cache:
        seen, found, fence = {}, set(), False
        for line in read(path).split("\n"):
            if line.startswith("```"):
                fence = not fence
            elif not fence and re.match(r"^#{1,6} ", line):
                found.add(slug(re.sub(r"^#{1,6} ", "", line), seen))
        for a in re.findall(r"<a (?:name|id)=\"([^\"]+)\"", read(path)):
            found.add(a)
        cache[path] = found
    return cache[path]


def doc_files(root):
    out = []
    for base, dirs, files in os.walk(os.path.join(root, "docs")):
        out += [os.path.join(base, f) for f in files if f.endswith(".md")]
    for name in ("README.md", "AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md"):
        if os.path.exists(os.path.join(root, name)):
            out.append(os.path.join(root, name))
    rules = os.path.join(root, ".claude", "rules")
    if os.path.isdir(rules):
        out += [os.path.join(rules, f) for f in os.listdir(rules) if f.endswith(".md")]
    return sorted(out)


CITED_STEP = re.compile(r"`([0-4]\.\d+\.\d+[a-z]?)`")


def check_cited_steps(root, steps, findings):
    """Every microstep ID cited in backticks anywhere in the docs names a real microstep."""
    for path in doc_files(root):
        rel = os.path.relpath(path, root)
        if rel.startswith("docs" + os.sep + "requirements"):
            continue
        for i, line in enumerate(read(path).split("\n"), 1):
            for sid in CITED_STEP.findall(line):
                if sid not in steps:
                    findings.append("%s:%d: cites microstep %s, which does not exist" % (rel, i, sid))


def check_links(root, findings):
    cache = {}
    for path in doc_files(root):
        rel = os.path.relpath(path, root)
        text = re.sub(r"```.*?```", lambda m: "\n" * m.group(0).count("\n"), read(path), flags=re.S)
        for i, line in enumerate(text.split("\n"), 1):
            line = re.sub(r"`[^`]*`", "", line)
            for target in LINK.findall(line):
                if re.match(r"^[a-z]+:", target):
                    continue
                file_part, _, anchor = target.partition("#")
                dest = os.path.normpath(os.path.join(os.path.dirname(path), file_part)) if file_part else path
                inside = os.path.relpath(dest, root)
                if inside.split(os.sep)[0] in APPS:
                    findings.append("%s:%d: link into the %s repository (%s) — cite it as a code span, it moves"
                                    % (rel, i, inside.split(os.sep)[0], target))
                    continue
                if inside.startswith(".."):
                    findings.append("%s:%d: link leaves the repository (%s)" % (rel, i, target))
                    continue
                if not os.path.exists(dest):
                    findings.append("%s:%d: broken link %s" % (rel, i, target))
                elif anchor and dest.endswith(".md") and anchor not in anchors(dest, cache):
                    findings.append("%s:%d: link %s names no heading in %s" % (rel, i, target, inside))


def git(args, cwd, check=True):
    p = subprocess.run(["git"] + args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if check and p.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(args), p.stderr.strip()))
    return p


class Pins:
    """The application commits the umbrella pins, fetched only when a done step needs them."""

    def __init__(self, root):
        self.root, self.repos, self.tmp = root, {}, None

    def commit(self, app):
        out = git(["ls-files", "-s", app], self.root, check=False).stdout.split()
        return out[1] if len(out) >= 2 else None

    def grep(self, app, name):
        if app == "umbrella":
            return git(["grep", "-I", "-n", "-F", "-e", name, "HEAD", "--"] + TEST_PATHS[app], self.root, check=False).stdout
        sha = self.commit(app)
        if not sha:
            raise RuntimeError("the umbrella pins no %s commit" % app)
        repo = self.repos.get(app)
        if repo is None:
            local = os.path.join(self.root, app)
            if os.path.exists(os.path.join(local, ".git")) and \
                    git(["cat-file", "-e", sha + "^{commit}"], local, check=False).returncode == 0:
                repo = local
            else:
                url = git(["config", "-f", ".gitmodules", "submodule.%s.url" % app], self.root).stdout.strip()
                self.tmp = self.tmp or tempfile.mkdtemp(prefix="check-plan-")
                repo = os.path.join(self.tmp, app)
                git(["init", "-q", repo], self.root)
                git(["remote", "add", "origin", url], repo)
                # every commit (for ancestry checks), blobs on demand (for grep and show)
                git(["fetch", "-q", "--filter=blob:none", "origin", sha], repo)
            self.repos[app] = repo
        return git(["grep", "-I", "-n", "-F", "-e", name, sha, "--"] + TEST_PATHS[app], repo, check=False).stdout

    def _repo_and_rev(self, app):
        if app == "umbrella":
            return self.root, "HEAD"
        self.grep(app, "check-plan-probe")          # makes sure the pinned commit is present
        return self.repos[app], self.commit(app)

    def show(self, app, path):
        repo, rev = self._repo_and_rev(app)
        return git(["show", "%s:%s" % (rev, path)], repo, check=False).stdout

    def contains(self, app, commit):
        repo, rev = self._repo_and_rev(app)
        if app == "umbrella" and git(["rev-parse", "--is-shallow-repository"], repo).stdout.strip() == "true":
            git(["fetch", "-q", "--unshallow"], repo, check=False)
        return git(["merge-base", "--is-ancestor", commit, rev], repo, check=False).returncode == 0

    def close(self):
        if self.tmp:
            shutil.rmtree(self.tmp, ignore_errors=True)


def declared(name, hit, pins, app, cache):
    """Whether a git-grep hit (rev:path:line:text) is a test declaration, not a comment or a stray mention."""
    m = re.match(r"^[^:]+:(.+?):(\d+):", hit)          # rev:path:line:text
    if not m:
        return False, "", "", 0
    path, lineno = m.group(1), int(m.group(2))
    if (app, path) not in cache:
        cache[(app, path)] = pins.show(app, path).split("\n")
    lines = cache[(app, path)]
    line = lines[lineno - 1] if 0 < lineno <= len(lines) else ""
    if COMMENT.match(line):
        return False, line, path, lineno
    if app == "umbrella":   # quoted (a self-test label), a Python test method, or a shell function
        named = re.search(r"""['"`]%s['"`]|\bdef\s+%s\s*\(|^\s*%s\s*\(\)""" % ((re.escape(name),) * 3), line)
        return bool(named), line, path, lineno
    if not re.search(r"""['"`][^'"`\n]*%s""" % re.escape(name), line):
        return False, line, path, lineno
    window = "\n".join(lines[max(0, lineno - 4):lineno])
    return bool(re.search(r"""\b(?:x?it|x?test)\b[\w.]*(?:\([^()]*\))?\s*\(\s*['"`]""", window)), window, path, lineno


def check_done_tests(steps, rows, pins, findings):
    cache = {}
    for sid, s in steps.items():
        if rows.get(sid, {}).get("status") != "done":
            continue
        for name in s.tests:
            found = False
            for app in s.repos:
                try:
                    hits = [h for h in pins.grep(app, name).split("\n") if h]
                except RuntimeError as err:
                    findings.append("%s is done but its tests cannot be checked: %s" % (sid, err))
                    continue
                for h in hits:
                    ok, context, path, lineno = declared(name, h, pins, app, cache)
                    if not ok or not path:
                        continue
                    found = True
                    lines = cache[(app, path)]
                    if path.endswith(JS_FILES):
                        if SKIPPED.search(context):
                            findings.append("%s is done but test %s is skipped, todo or focused (%s)" % (sid, name, path))
                        elif SKIPPED_SUITE.search("\n".join(lines)):
                            findings.append("%s is done but test %s sits in a file with a skipped or focused suite (%s)"
                                            % (sid, name, path))
                    elif path.endswith(".py") and re.search(r"\bdef\s+%s\s*\(" % re.escape(name), context) \
                            and any(PY_SKIP.match(l) for l in lines[max(0, lineno - 4):lineno - 1]):
                        findings.append("%s is done but test %s is skipped (%s)" % (sid, name, path))
            if not found:
                findings.append("%s is done but no test declares %s in %s at the pinned commit"
                                % (sid, name, " or ".join(s.repos)))


def github_pull(repo, number):
    req = urllib.request.Request("https://api.github.com/repos/OmarSweiti/%s/pulls/%s" % (repo, number),
                                 headers={"Accept": "application/vnd.github+json", "User-Agent": "check-plan"})
    if os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.load(resp)
    return {"merged": bool(data.get("merged")), "merge_commit_sha": data.get("merge_commit_sha")}


PULL_LOOKUP = github_pull


def check_done_evidence(steps, rows, pins, findings):
    """Online: every cited PR is merged, and its merge commit is in the history the umbrella pins."""
    app_of = {v: k for k, v in REPO_OF.items()}
    for sid, r in rows.items():
        if r.get("status") != "done" or sid not in steps:
            continue
        for repo, number in PR_PARTS.findall(r["evidence"]):
            try:
                pr = PULL_LOOKUP(repo, number)
            except Exception as err:  # network or rate limit: say so rather than pass silently
                findings.append("%s cites %s#%s, which could not be verified: %s" % (sid, repo, number, err))
                continue
            if not pr["merged"]:
                findings.append("%s cites %s#%s, which is not merged" % (sid, repo, number))
            elif not pins.contains(app_of[repo], pr["merge_commit_sha"]):
                findings.append("%s cites %s#%s, whose merge commit is not in the pinned history" % (sid, repo, number))


# ------------------------------------------------------------------------- generated

def replace_block(text, name, body):
    pattern = re.compile(r"(<!-- plan:%s:begin -->\n).*?(<!-- plan:%s:end -->)" % (name, name), re.S)
    if not pattern.search(text):
        return None
    return pattern.sub(lambda m: m.group(1) + body + m.group(2), text)


def status_of(rows, sid):
    return rows.get(sid, {}).get("status", "todo")


def render_progress(steps, rows):
    out = ["| Step | Title | Repo | Status | Evidence |", "|---|---|---|---|---|"]
    for sid, s in steps.items():
        r = rows.get(sid, {})
        out.append("| %s | %s | %s | %s | %s |" % (sid, s.title.replace("|", "\\|"), " + ".join(s.repos),
                                                 r.get("status", "todo"), r.get("evidence", "")))
    return "\n".join(out) + "\n"


def milestone_lines(steps, rows, milestone):
    """The milestone's progress, remaining ceiling hours and the steps ready in build order."""
    ids = [sid for sid, _ in milestone if sid in steps]
    if not ids:
        return []
    done = sum(1 for sid in ids if status_of(rows, sid) == "done")
    left = sum(WEIGHT.get(steps[sid].size, 0) for sid in ids if status_of(rows, sid) != "done")
    ready = [sid for sid in ids if status_of(rows, sid) == "todo"
             and all(status_of(rows, d) == "done" for d in steps[sid].deps)]
    return ["**Demo milestone** ([build order](demo-milestone.md)) — %d of %d microsteps done; %d–%d engineering "
            "hours left before the reserve." % (done, len(ids), left // 2, left),
            "Next in build order (every dependency done): %s." % (
                ", ".join("`%s`" % x for x in ready[:8]) or "none")
            + (" … and %d more." % (len(ready) - 8) if len(ready) > 8 else "")]


def render_milestone(steps, rows, milestone):
    lines = milestone_lines(steps, rows, milestone)
    if not lines:
        return "The milestone lists no step.\n"
    out = [lines[0].replace(" ([build order](demo-milestone.md))", ""), "", lines[1], "",
           "| Stage | Step | Title | Repo | Size | Status |", "|---|---|---|---|---|---|"]
    for sid, stage in milestone:
        if sid in steps:
            s = steps[sid]
            out.append("| %s | %s | %s | %s | %s | %s |" % (stage, sid, s.title.replace("|", "\\|"), " + ".join(s.repos),
                                                          s.size, status_of(rows, sid)))
    return "\n".join(out) + "\n"


def render_frontier(steps, rows, milestone=()):
    live = [s for s in steps.values() if status_of(rows, s.id) not in ("done", "superseded")]
    if not live:
        return "Every microstep is done.\n"
    phase = min(s.phase for s in live)
    in_phase = [s for s in steps.values() if s.phase == phase]
    done = sum(1 for s in in_phase if status_of(rows, s.id) == "done")
    total_done = sum(1 for s in steps.values() if status_of(rows, s.id) == "done")
    ready = [s.id for s in in_phase if status_of(rows, s.id) == "todo"
             and all(status_of(rows, d) == "done" for d in s.deps)]
    doing = [s.id for s in in_phase if status_of(rows, s.id) == "in-progress"]
    blocked = [s.id for s in in_phase if status_of(rows, s.id) == "blocked"]
    lines = milestone_lines(steps, rows, milestone) + [
             "**Phase %d** — %d of %d microsteps done (%d of %d across all phases)."
             % (phase, done, len(in_phase), total_done, len(steps)),
             "In progress: %s." % (", ".join("`%s`" % x for x in doing) or "none"),
             "Ready now (every dependency done): %s." % (", ".join("`%s`" % x for x in ready[:12]) or "none")
             + (" … and %d more." % (len(ready) - 12) if len(ready) > 12 else ""),
             "Blocked: %s." % (", ".join("`%s`" % x for x in blocked) or "none")]
    return "\n".join(lines) + "\n"


def render_catalog(steps, rows):
    out = ["| Test | Microstep | Repo | Status |", "|---|---|---|---|"]
    for sid, s in steps.items():
        for t in s.tests:
            out.append("| `%s` | %s | %s | %s |" % (t, sid, " + ".join(s.repos), status_of(rows, sid)))
    return "\n".join(out) + "\n"


def render_trace(steps, rows, defined, deferred):
    owners = OrderedDict((rid, []) for rid in defined)
    for s in steps.values():
        for rid in s.reqs:
            if rid in owners and s.id not in owners[rid]:
                owners[rid].append(s.id)
    out = ["| Requirement | Source | Owning microsteps | Done |", "|---|---|---|---|"]
    for rid, doc in defined.items():
        own = owners[rid]
        if own:
            done = sum(1 for x in own if status_of(rows, x) == "done")
            out.append("| %s | %s | %s | %d/%d |" % (rid, doc.split("_")[2].replace(".md", ""),
                                                   ", ".join(own), done, len(own)))
        else:
            out.append("| %s | %s | deferred — %s | — |" % (rid, doc.split("_")[2].replace(".md", ""),
                                                          deferred.get(rid, "UNOWNED")))
    return "\n".join(out) + "\n"


GENERATED = [
    ("docs/implementation/progress.md", "progress", lambda st, ro, de, df, mi: render_progress(st, ro)),
    ("docs/implementation/README.md", "frontier", lambda st, ro, de, df, mi: render_frontier(st, ro, mi)),
    ("docs/reference/test-catalog.md", "catalog", lambda st, ro, de, df, mi: render_catalog(st, ro)),
    ("docs/reference/traceability.md", "trace", lambda st, ro, de, df, mi: render_trace(st, ro, de, df)),
    (MILESTONE, "milestone", lambda st, ro, de, df, mi: render_milestone(st, ro, mi)),  # only when it exists
]


def run(root, write_mode=False, check_tests=True, quiet=False, online=None):
    if online is None:
        online = os.environ.get("CHECK_PLAN_ONLINE") == "1" or os.environ.get("GITHUB_ACTIONS") == "true"
    findings = []
    steps = load_plan(root, findings)
    rows = load_progress(root, findings)
    defined = defined_requirements(root)
    deferred = deferred_requirements(root)
    milestone = load_milestone(root, steps, rows, findings)
    for rel, name, render in GENERATED:
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            if rel != MILESTONE:
                findings.append("%s: missing" % rel)
            continue
        text = read(path)
        new = replace_block(text, name, render(steps, rows, defined, deferred, milestone))
        if new is None:
            findings.append("%s: no <!-- plan:%s:begin/end --> block" % (rel, name))
        elif new != text:
            if write_mode:
                write(path, new)
                if not quiet:
                    print("check-plan: regenerated %s" % rel)
                if name == "progress":
                    rows = load_progress(root, [])
            else:
                findings.append("%s: the %s block is stale (run: python3 scripts/check-plan.py --write)" % (rel, name))
    check_graph(steps, findings)
    check_tests_unique(steps, findings)
    check_progress(steps, rows, findings)
    check_requirements(steps, defined, deferred, findings)
    check_checksums(root, findings)
    check_links(root, findings)
    check_cited_steps(root, steps, findings)
    if check_tests:
        pins = Pins(root)
        try:
            check_done_tests(steps, rows, pins, findings)
            if online:
                check_done_evidence(steps, rows, pins, findings)
        finally:
            pins.close()
    return steps, rows, findings


# ------------------------------------------------------------------------- self-test

FIXTURE = {
    "docs/requirements/01_X_BRD.md": "BR-OBJ-01 BR-RULE-01\n",
    "docs/requirements/04_X_SRS.md": "SR-CORE-001 SR-CORE-002 SR-CORE-003 TEST-001\n",
    "docs/implementation/00-master-plan.md": "<!-- plan:deferred:begin -->\n| TEST-001 | covered by every gate |\n<!-- plan:deferred:end -->\n",
    "docs/implementation/phase-0-x.md": (
        "# Phase 0\n\n## Group 0.1 — A\n\n"
        "### 0.1.1 — First\n**Repo:** umbrella · **Size:** S · **Depends on:** — · **Requirements:** BR-OBJ-01, SR-CORE-001..002\n"
        "**Tests:** `first_step_proves_itself`\n**Verify:** `true`\n**Done when:** yes.\n\n"
        "### 0.1.2 — Second\n**Repo:** umbrella · **Size:** M · **Depends on:** `0.1.1` · **Requirements:** BR-RULE-01, SR-CORE-003\n"
        "**Tests:** `second_step_proves_itself`\n**Verify:** `true`\n**Done when:** yes.\n"),
    "docs/implementation/progress.md": "# Progress\n\n<!-- plan:progress:begin -->\n<!-- plan:progress:end -->\n",
    "docs/implementation/README.md": "# Index\n\n[plan](phase-0-x.md#011--first)\n\n<!-- plan:frontier:begin -->\n<!-- plan:frontier:end -->\n",
    "docs/reference/test-catalog.md": "# Tests\n\n<!-- plan:catalog:begin -->\n<!-- plan:catalog:end -->\n",
    "docs/reference/traceability.md": "# Trace\n\n<!-- plan:trace:begin -->\n<!-- plan:trace:end -->\n",
    "scripts/selftest.sh": "echo \"first_step_proves_itself\"\n",
}


def make_fixture(tmp, overrides=None):
    files = dict(FIXTURE)
    files.update(overrides or {})
    for rel, text in files.items():
        path = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        write(path, text)
    src = os.path.join(tmp, "docs", "requirements", "04_X_SRS.md")
    with open(src, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    write(os.path.join(tmp, "docs", "requirements", "README.md"), "| `04_X_SRS.md` | `%s` |\n" % digest)
    git(["init", "-q"], tmp)
    git(["-c", "user.name=t", "-c", "user.email=t@example.test", "add", "-A"], tmp)
    git(["-c", "user.name=t", "-c", "user.email=t@example.test", "commit", "-qm", "fixture"], tmp)


def self_test():
    failures = []

    def expect(label, mutate, needle, regenerate=False, pulls=None):
        tmp = tempfile.mkdtemp(prefix="check-plan-self-")
        try:
            make_fixture(tmp)
            run(tmp, write_mode=True, quiet=True)
            mutate(tmp)
            git(["add", "-A"], tmp)
            git(["-c", "user.name=t", "-c", "user.email=t@example.test", "commit", "-qm", "mutate", "--allow-empty"], tmp)
            global PULL_LOOKUP
            saved = PULL_LOOKUP
            if pulls is not None:
                head = git(["rev-parse", "HEAD"], tmp).stdout.strip()
                PULL_LOOKUP = lambda repo, number: {k: (head if v == "HEAD" else v) for k, v in pulls.items()}
            try:
                _, _, found = run(tmp, write_mode=regenerate, quiet=True, online=pulls is not None)
            finally:
                PULL_LOOKUP = saved
            hit = [f for f in found if needle in f]
            if needle == "" and found:
                failures.append("%s: expected no findings, got %s" % (label, found))
            elif needle and not hit:
                failures.append("%s: expected a finding containing '%s', got %s" % (label, needle, found))
            else:
                print("  ok   %s" % label)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def edit(rel, old, new):
        def f(tmp):
            path = os.path.join(tmp, rel)
            text = read(path)
            assert old in text, (rel, old)
            write(path, text.replace(old, new, 1))
        return f

    prog = "docs/implementation/progress.md"
    phase = "docs/implementation/phase-0-x.md"
    pr = "https://github.com/OmarSweiti/Players_Platform/pull/7"
    expect("a_clean_plan_passes", lambda t: None, "")
    expect("a_missing_progress_row_is_refused", edit(prog, "| 0.1.2 | Second | umbrella | todo |  |\n", ""), "no row for 0.1.2")
    expect("an_unknown_status_is_refused", edit(prog, "| 0.1.1 | First | umbrella | todo |", "| 0.1.1 | First | umbrella | finished |"), "has status 'finished'")
    expect("a_done_step_without_a_merged_pr_is_refused", edit(prog, "| 0.1.1 | First | umbrella | todo |", "| 0.1.1 | First | umbrella | done |"), "cites no merged PR")
    expect("a_done_step_with_an_undone_dependency_is_refused",
           edit(prog, "| 0.1.2 | Second | umbrella | todo |  |", "| 0.1.2 | Second | umbrella | done | %s |" % pr), "dependency 0.1.1 is todo")
    expect("a_done_step_whose_named_test_is_missing_is_refused",
           edit(prog, "| 0.1.2 | Second | umbrella | todo |  |", "| 0.1.2 | Second | umbrella | done | %s |" % pr), "no test declares second_step_proves_itself")
    expect("a_done_step_with_its_tests_present_passes",
           edit(prog, "| 0.1.1 | First | umbrella | todo |  |", "| 0.1.1 | First | umbrella | done | %s |" % pr), "",
           regenerate=True)
    expect("a_skipped_named_test_is_refused", lambda t: (
        edit(prog, "| 0.1.1 | First | umbrella | todo |  |", "| 0.1.1 | First | umbrella | done | %s |" % pr)(t),
        write(os.path.join(t, "scripts", "selftest.spec.ts"), "it.skip('first_step_proves_itself', () => {})\n")),
        "skipped, todo or focused")
    expect("a_dangling_dependency_is_refused", edit(phase, "`0.1.1` ·", "`0.1.9` ·"), "depends on 0.1.9, which does not exist")
    expect("a_duplicate_step_is_refused", edit(phase, "### 0.1.2 — Second", "### 0.1.1 — Second"), "defined twice")
    expect("an_unowned_requirement_is_refused", edit(phase, ", SR-CORE-003", ""), "SR-CORE-003")
    expect("an_invented_requirement_is_refused", edit(phase, "SR-CORE-003", "SR-CORE-003, SR-CORE-042"), "cites SR-CORE-042")
    expect("a_malformed_test_name_is_refused", edit(phase, "`second_step_proves_itself`", "`Second`"), "not a lower_snake test name")
    expect("a_stale_generated_block_is_refused", edit(phase, "— Second", "— Second, renamed"), "block is stale")
    expect("an_edited_frozen_requirement_is_refused", edit("docs/requirements/04_X_SRS.md", "TEST-001", "TEST-001 edited"), "checksum differs")
    expect("a_broken_link_or_anchor_is_refused", edit("docs/implementation/README.md", "phase-0-x.md#011--first", "phase-9.md"), "broken link")
    expect("a_broken_anchor_is_refused", edit("docs/implementation/README.md", "#011--first", "#nowhere"), "names no heading")
    expect("a_citation_of_a_missing_step_is_refused", edit("docs/implementation/README.md", "# Index", "# Index\n\nSee `0.1.7`."), "cites microstep 0.1.7")
    expect("a_link_into_an_application_is_refused", edit("docs/implementation/README.md", "[plan](phase-0-x.md#011--first)", "[x](../../backend/src/main.ts)"), "link into the backend")
    done1 = edit(prog, "| 0.1.1 | First | umbrella | todo |  |", "| 0.1.1 | First | umbrella | done | %s |" % pr)
    expect("a_name_only_in_a_comment_is_refused", lambda t: (
        done1(t), write(os.path.join(t, "scripts", "selftest.sh"), '# "first_step_proves_itself"\n')),
        "no test declares first_step_proves_itself")
    expect("a_skipped_suite_is_refused", lambda t: (
        done1(t), write(os.path.join(t, "scripts", "selftest.spec.ts"),
                        "describe" + ".skip('suite', () => {\n  it('first_step_proves_itself', () => {})\n})\n")),
        "skipped or focused suite")
    expect("a_skipped_python_test_is_refused", lambda t: (
        done1(t), write(os.path.join(t, "scripts", "test_selftest.py"),
                        "import unittest\n\n\nclass T(unittest.TestCase):\n    @unittest.skip('later')\n"
                        "    def first_step_proves_itself(self):\n        pass\n")),
        "is skipped (scripts/test_selftest.py)")
    expect("a_two_repository_step_needs_a_pr_per_repository", lambda t: (
        done1(t), edit(phase, "### 0.1.1 — First\n**Repo:** umbrella", "### 0.1.1 — First\n**Repo:** umbrella + backend")(t)),
        "cites no merged PR for backend")
    expect("an_unmerged_pr_is_refused", done1, "is not merged", pulls={"merged": False, "merge_commit_sha": None})
    expect("a_pr_outside_the_pinned_history_is_refused", done1, "not in the pinned history",
           pulls={"merged": True, "merge_commit_sha": "0" * 40})
    expect("a_merged_pr_in_the_pinned_history_passes", done1, "", regenerate=True,
           pulls={"merged": True, "merge_commit_sha": "HEAD"})
    expect("a_step_without_a_size_is_refused", edit(phase, " · **Size:** M", ""), "has no **Size:** of S, M or L")

    def milestone(*rows):
        body = "".join("| %s — a stage | `%s` |\n" % (stage, sid) for sid, stage in rows)
        return lambda t: write(os.path.join(t, MILESTONE),
                               "# Demo\n\n<!-- milestone:steps:begin -->\n| Stage | Steps |\n|---|---|\n%s"
                               "<!-- milestone:steps:end -->\n\n<!-- plan:milestone:begin -->\n<!-- plan:milestone:end -->\n"
                               % body)
    expect("a_sound_milestone_passes", milestone(("0.1.1", "A"), ("0.1.2", "B")), "", regenerate=True)
    expect("a_milestone_step_with_an_unfinished_outside_dependency_is_refused", milestone(("0.1.2", "A")),
           "neither in the milestone nor done", regenerate=True)
    expect("a_milestone_out_of_build_order_is_refused", milestone(("0.1.2", "A"), ("0.1.1", "A")),
           "listed before its dependency", regenerate=True)
    expect("a_milestone_naming_a_missing_step_is_refused", milestone(("0.1.1", "A"), ("0.1.9", "A")),
           "step 0.1.9 does not exist", regenerate=True)
    expect("a_milestone_whose_last_step_misses_a_step_is_refused", lambda t: (
        edit(phase, "**Depends on:** `0.1.1` ·", "**Depends on:** — ·")(t), milestone(("0.1.1", "A"), ("0.1.2", "B"))(t)),
        "does not depend on 0.1.1", regenerate=True)
    expect("a_stale_milestone_block_is_refused", lambda t: (
        milestone(("0.1.1", "A"), ("0.1.2", "A"))(t), run(t, write_mode=True, quiet=True),
        edit(prog, "| 0.1.1 | First | umbrella | todo |  |", "| 0.1.1 | First | umbrella | done | %s |" % pr)(t)),
        "the milestone block is stale")
    if failures:
        print("\n".join("  FAIL " + f for f in failures))
        return 1
    print("check-plan: every check still refuses what it must")
    return 0


def main(argv):
    if argv == ["--self-test"]:
        return self_test()
    if argv not in ([], ["--write"]):
        print(__doc__.strip().split("\n\n")[0], file=sys.stderr)
        return 2
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    steps, rows, findings = run(root, write_mode=argv == ["--write"])
    for f in findings:
        print("check-plan: " + f)
    if findings:
        print("check-plan: %d finding(s)" % len(findings))
        return 1
    done = sum(1 for r in rows.values() if r["status"] == "done")
    print("check-plan: %d microsteps, %d done; plan, progress, requirements and links agree" % (len(steps), done))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
