#!/usr/bin/env python3
"""The local stack keeps its promises (plan step 0.2.1; ADR-0013).

  python3 scripts/check-stack.py              check infra/compose.yaml
  python3 scripts/check-stack.py --self-test  prove every rule refuses what it must

The rules run over the model Compose itself resolves (`docker compose config`, with
the development values of infra/.env.example), so defaults and interpolation are
read exactly as `just up` reads them:

  1. every image is pinned by digest — or, for a service built here (the worker, 0.7.6), it
     is built from the pinned backend, whose Dockerfile pins every base image by digest,
     and is never pulled;
  2. every published port binds to 127.0.0.1 — nothing is reachable from another machine;
  3. every service declares its own health check, so `just up` can wait for it;
  4. PostgreSQL runs the digest the pinned backend's CI and migration replay run.
"""
import importlib.util
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPOSE = ["docker", "compose", "--file", "infra/compose.yaml", "--env-file", "infra/.env.example"]
PINNED = re.compile(r"@(sha256:[0-9a-f]{64})$")
POSTGRES_PIN = re.compile(r"\bpostgres:[^@\s\"']*@(sha256:[0-9a-f]{64})")
BACKEND_FILES = (".github/workflows/ci.yml", "justfile", "Dockerfile")
# The checkouts a service may be built from: the pinned backend alone.
BUILT_FROM = ("backend",)
FROM = re.compile(r"^FROM\s+(?:--\S+\s+)*(\S+)(?:\s+AS\s+(\S+))?", re.M | re.I)
ARG = re.compile(r"^ARG\s+(\w+)=(\S+)", re.M)


def unpinned_bases(dockerfile):
    """The base images a Dockerfile builds on that are not pinned by digest (its own stages aside)."""
    args = dict(ARG.findall(dockerfile))
    stages, unpinned = set(), []
    for base, stage in FROM.findall(dockerfile):
        image = re.sub(r"\$\{?(\w+)\}?", lambda m: args.get(m.group(1), m.group(0)), base)
        if image not in stages and not PINNED.search(image):
            unpinned.append(image)
        if stage:
            stages.add(stage)
    return unpinned


def findings_for(model, backend_files):
    """Every broken promise in a resolved compose model, as readable findings."""
    findings = []
    services = model.get("services") or {}
    if not services:
        findings.append("infra/compose.yaml defines no service")
    for name, service in sorted(services.items()):
        image = service.get("image") or ""
        build = service.get("build")
        if build:
            context = os.path.relpath((build or {}).get("context") or "", ROOT)
            if context not in BUILT_FROM:
                findings.append("%s: built from %r, not the pinned backend" % (name, context))
            elif not (backend_files.get("Dockerfile") or "").strip():
                findings.append("%s: the pinned backend has no Dockerfile" % name)
            else:
                for base in unpinned_bases(backend_files["Dockerfile"]):
                    findings.append("%s: the backend's Dockerfile builds on %r, not pinned by digest" % (name, base))
            if service.get("pull_policy") != "build":
                findings.append("%s: is built here, so it must never be pulled (pull_policy: build)" % name)
        elif not PINNED.search(image):
            findings.append("%s: image %r is not pinned by digest (name:tag@sha256:…)" % (name, image))
        for port in service.get("ports") or []:
            if port.get("published") and port.get("host_ip") != "127.0.0.1":
                findings.append("%s: port %s is published on %s, not 127.0.0.1" % (
                    name, port.get("published"), port.get("host_ip") or "every interface"))
        check = service.get("healthcheck") or {}
        if check.get("disable") or not check.get("test"):
            findings.append("%s: declares no health check" % name)

    stack = PINNED.search((services.get("postgres") or {}).get("image") or "")
    if not stack:
        findings.append("postgres: the stack has no PostgreSQL service pinned by digest")
        return findings
    for path in (".github/workflows/ci.yml", "justfile"):
        found = sorted(set(POSTGRES_PIN.findall(backend_files.get(path) or "")))
        if not found:
            findings.append("backend %s pins no PostgreSQL digest" % path)
        elif found != [stack.group(1)]:
            findings.append("backend %s runs PostgreSQL %s, the stack %s — ADR-0013 wants one digest everywhere" % (
                path, ", ".join(found), stack.group(1)))
    return findings


def pinned_backend_files():
    """The backend files at the commit the umbrella pins, read the way the plan check reads them."""
    spec = importlib.util.spec_from_file_location("check_plan", os.path.join(ROOT, "scripts", "check-plan.py"))
    check_plan = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(check_plan)
    pins = check_plan.Pins(ROOT)
    try:
        return {path: pins.show("backend", path) for path in BACKEND_FILES}
    finally:
        pins.close()


def check():
    resolved = subprocess.run(COMPOSE + ["config", "--format", "json"], cwd=ROOT, capture_output=True, text=True)
    if resolved.returncode != 0:
        print("check-stack: docker compose cannot read infra/compose.yaml:\n" + resolved.stderr.strip())
        return 1
    model = json.loads(resolved.stdout)
    findings = findings_for(model, pinned_backend_files())
    for finding in findings:
        print("check-stack: " + finding)
    if findings:
        print("check-stack: %d finding(s)" % len(findings))
        return 1
    print("check-stack: %d services — every image a digest or built from the pinned backend, every port "
          "on 127.0.0.1, every service health-checked, PostgreSQL the backend's digest" % len(model["services"]))
    return 0


def self_test():
    digest = "sha256:" + "a" * 64
    other = "sha256:" + "b" * 64
    dockerfile = ("ARG NODE_IMAGE=node:24.19.0-alpine@%s\nFROM ${NODE_IMAGE} AS build\nRUN npm ci\n"
                  "FROM ${NODE_IMAGE}\nCOPY --from=build /app/dist ./dist\n" % digest)
    backend = {".github/workflows/ci.yml": "image: postgres:18@%s # 18.6" % digest,
               "justfile": "docker run postgres:18@%s" % digest,
               "Dockerfile": dockerfile}

    def service(**overrides):
        base = {"image": "postgres:18.6@" + digest,
                "ports": [{"host_ip": "127.0.0.1", "published": "5432", "target": 5432}],
                "healthcheck": {"test": ["CMD", "pg_isready"]}}
        base.update(overrides)
        return base

    def model(**services):
        return {"services": services or {"postgres": service()}}

    def built(**overrides):
        base = {"build": {"context": os.path.join(ROOT, "backend")}, "image": "sadara-backend:local",
                "pull_policy": "build", "healthcheck": {"test": ["CMD-SHELL", "true"]}}
        base.update(overrides)
        return base

    cases = [
        ("a stack that keeps every promise", model(), backend, 0),
        ("an image with a tag and no digest", model(postgres=service(), cache=service(image="valkey/valkey:9")),
         backend, 1),
        ("a port on every interface", model(postgres=service(ports=[{"published": "5432", "target": 5432}])),
         backend, 1),
        ("a port on 0.0.0.0", model(postgres=service(ports=[{"host_ip": "0.0.0.0", "published": "5432"}])),
         backend, 1),
        ("a service without a health check", model(postgres=service(), mail=service(healthcheck=None)), backend, 1),
        ("a disabled health check", model(postgres=service(healthcheck={"disable": True})), backend, 1),
        ("the backend's CI on another PostgreSQL digest", model(),
         dict(backend, **{".github/workflows/ci.yml": "image: postgres:18@" + other}), 1),
        ("a backend file with no PostgreSQL digest", model(), dict(backend, justfile="docker run postgres:18"), 1),
        ("a stack without PostgreSQL", {"services": {"mail": service(image="axllent/mailpit:v1@" + digest)}},
         backend, 1),
        ("an empty stack", {"services": {}}, backend, 2),
        ("a worker built from the pinned backend, its bases pinned", model(postgres=service(), worker=built()),
         backend, 0),
        ("a built service whose Dockerfile's base is a tag", model(postgres=service(), worker=built()),
         dict(backend, Dockerfile="FROM node:24-alpine\n"), 1),
        ("a built service that may be pulled", model(postgres=service(), worker=built(pull_policy=None)),
         backend, 1),
        ("a service built from elsewhere",
         model(postgres=service(), worker=built(build={"context": os.path.join(ROOT, "frontend")})), backend, 1),
        ("a built service without a health check", model(postgres=service(), worker=built(healthcheck=None)),
         backend, 1),
    ]
    failures = 0
    for label, compose_model, files, expected in cases:
        got = len(findings_for(compose_model, files))
        ok = got == expected
        failures += not ok
        print("  %s  %s (%d finding%s)" % ("ok  " if ok else "FAIL", label, got, "" if got == 1 else "s"))
    print("check-stack self-test: %s" % ("every rule refuses what it must" if not failures else "%d FAILED" % failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(self_test() if sys.argv[1:] == ["--self-test"] else check())
