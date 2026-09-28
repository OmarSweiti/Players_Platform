#!/usr/bin/env bash
# The platform repository pins one commit of each application repository.
# A pin must be a commit the application's OWN flow branches keep: squash
# merges and delete-branch-on-merge orphan every work-branch commit, so a pin
# to one rots silently once that branch is gone. The target branch decides
# which application branches count, so releases happen in order:
#
#   platform development ← the app's development, staging or main
#   platform staging     ← the app's staging or main   (promote the apps first)
#   platform main        ← the app's main              (release the apps first)
#
# Fails closed: a pin it cannot fetch or place is a pin it refuses.
#
#   ./scripts/check-submodules.sh <target-branch>
#   ./scripts/check-submodules.sh --self-test
set -euo pipefail

usage() {
  echo "usage: $0 <target-branch> | --self-test" >&2
  exit 2
}

accepted_branches() { # the application branches a pin on <target> may come from
  case "$1" in
    main) echo "main" ;;
    staging) echo "staging main" ;;
    *) echo "development staging main" ;;
  esac
}

check() {
  local target=$1 accepted tmp key name path url sha branch found fetched refused=0 checked=0
  accepted=$(accepted_branches "$target")
  if [ ! -f .gitmodules ]; then
    echo "submodules: no .gitmodules — nothing to check"
    return 0
  fi
  tmp=$(mktemp -d "${TMPDIR:-/tmp}/check-submodules.XXXXXX")
  trap 'rm -rf "$tmp"; trap - RETURN' RETURN
  while read -r key path; do
    name=${key#submodule.}
    name=${name%.path}
    if ! url=$(git config -f .gitmodules --get "submodule.$name.url"); then
      echo "::error::submodules: $name has no url in .gitmodules; refusing closed" >&2
      refused=1
      continue
    fi
    sha=$(git ls-tree HEAD -- "$path" | awk '$2 == "commit" { print $3 }')
    if [ -z "$sha" ]; then
      echo "::error::submodules: no gitlink at '$path' for $name in HEAD; refusing closed" >&2
      refused=1
      continue
    fi
    checked=$((checked + 1))
    git init -q --bare "$tmp/$name.git"
    found='' fetched=''
    for branch in $accepted; do
      # Blob-less: ancestry needs commits, never file contents.
      if git -C "$tmp/$name.git" fetch -q --filter=blob:none "$url" "+refs/heads/$branch:refs/heads/$branch" 2>/dev/null; then
        fetched="$fetched $branch"
        if git -C "$tmp/$name.git" merge-base --is-ancestor "$sha" "refs/heads/$branch" 2>/dev/null; then
          found=$branch
          break
        fi
      fi
    done
    if [ -n "$found" ]; then
      echo "submodules: $path @ ${sha:0:12} is on $name's $found"
    elif [ -z "$fetched" ]; then
      echo "::error::submodules: could not fetch any of [$accepted] from $url; refusing closed" >&2
      refused=1
    else
      echo "::error::submodules: $path pins ${sha:0:12}, which none of $name's [$accepted] contains (fetched:$fetched)." >&2
      echo "  A platform $target pin must come from those branches: merge (and promote) the application first." >&2
      refused=1
    fi
  done < <(git config -f .gitmodules --get-regexp '^submodule\..*\.path$' || true)
  if [ "$checked" -eq 0 ] && [ "$refused" -eq 0 ]; then echo "submodules: .gitmodules declares none"; fi
  return "$refused"
}

self_test() {
  local pass=0 fail=0 tmp self app work super main_sha staging_sha dev_sha orphan_sha
  self="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
  tmp=$(mktemp -d "${TMPDIR:-/tmp}/check-submodules-test.XXXXXX")
  trap 'rm -rf "$tmp"; trap - RETURN' RETURN

  # An application repository: main ⊂ staging, main ⊂ development, plus a
  # work-branch commit that is never pushed — what a squash merge orphans.
  app="$tmp/app.git"
  work="$tmp/app-work"
  git init -q --bare "$app"
  git init -q -b main "$work"
  git -C "$work" config user.name t
  git -C "$work" config user.email t@t
  git -C "$work" commit -q --no-verify --allow-empty -m release
  main_sha=$(git -C "$work" rev-parse HEAD)
  git -C "$work" branch staging
  git -C "$work" branch development
  git -C "$work" switch -q staging
  git -C "$work" commit -q --no-verify --allow-empty -m candidate
  staging_sha=$(git -C "$work" rev-parse HEAD)
  git -C "$work" switch -q development
  git -C "$work" commit -q --no-verify --allow-empty -m integrated
  dev_sha=$(git -C "$work" rev-parse HEAD)
  git -C "$work" switch -q -c feat/x
  git -C "$work" commit -q --no-verify --allow-empty -m 'work in progress'
  orphan_sha=$(git -C "$work" rev-parse HEAD)
  git -C "$work" push -q "$app" main staging development 2>/dev/null

  # A platform repository pinning that application at app/.
  super="$tmp/super"
  git init -q -b development "$super"
  git -C "$super" config user.name t
  git -C "$super" config user.email t@t
  printf '[submodule "app"]\n\tpath = app\n\turl = file://%s\n' "$app" >"$super/.gitmodules"
  expect() { # expect <exit> <label> <target> <pinned-sha>
    local want=$1 label=$2 got=0
    git -C "$super" update-index --add --cacheinfo "160000,$4,app"
    git -C "$super" add .gitmodules
    git -C "$super" commit -q --no-verify --allow-empty -m pin
    (cd "$super" && bash "$self" "$3") >/dev/null 2>&1 || got=$?
    if [ "$got" -eq "$want" ]; then printf '  ok      %s\n' "$label"; pass=$((pass + 1))
    else printf '  FAILED  %s (wanted %s, got %s)\n' "$label" "$want" "$got"; fail=$((fail + 1)); fi
  }
  echo "submodule pins"
  expect 0 "development accepts the app's development" development "$dev_sha"
  expect 0 "development accepts the app's main" development "$main_sha"
  expect 1 "staging refuses a commit only the app's development has" staging "$dev_sha"
  expect 0 "staging accepts the app's staging" staging "$staging_sha"
  expect 1 "main refuses a commit only the app's staging has" main "$staging_sha"
  expect 0 "main accepts the app's main" main "$main_sha"
  expect 1 "a work-branch commit is refused, even on development" development "$orphan_sha"
  printf '[submodule "app"]\n\tpath = app\n\turl = file://%s\n' "$tmp/missing.git" >"$super/.gitmodules"
  expect 1 "an unreachable application repository fails closed" development "$dev_sha"
  printf '\n%s passed, %s failed\n' "$pass" "$fail"
  [ "$fail" -eq 0 ]
}

case "${1:-}" in
  --self-test) [ "$#" -eq 1 ] || usage; self_test ;;
  -* | '') usage ;;
  *) [ "$#" -eq 1 ] || usage; check "$1" ;;
esac
