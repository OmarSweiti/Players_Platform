#!/usr/bin/env bash
# Post validation evidence on a pull request (docs/implementation/02-development-workflow.md,
# "Validate"): the report you wrote — what was run, what was expected, what
# was seen — and its screenshots, for the PR's exact head commit.
#
#   ./scripts/publish-evidence.sh <PR URL> <report.md> [<screenshot dir>]
#
# 1. The report is refused if it carries a secret (gitleaks) or assistant
#    attribution.
# 2. The screenshots — PNG only, at most 25, each under 5 MB, named
#    [a-z0-9-]+.png — are committed to the evidence repository under
#    <repository>/pr-<n>/<head SHA>/ and pushed: the code repositories never
#    carry images.
# 3. The comment — the report, the screenshots linked at that evidence commit
#    so they can never change, and the marker the `validation` check reads —
#    is posted by the engineering app.
# 4. The `validation` check runs again for the head commit, and the script
#    reports its verdict.
set -euo pipefail

readonly EVIDENCE_REPO=OmarSweiti/Players_Platform_Evidence
readonly MAX_IMAGES=25 MAX_BYTES=$((5 * 1024 * 1024))
here=$(cd "$(dirname "$0")" && pwd)
usage="usage: publish-evidence.sh <PR URL> <report.md> [<screenshot dir>]"
url=${1:?$usage}
report=${2:?$usage}
shots=${3:-}
refuse() { echo "evidence: REFUSED — $*" >&2; exit 1; }

[[ "$url" =~ ^https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/pull/([0-9]+)$ ]] ||
  refuse "$url is not a pull request URL"
repo=${BASH_REMATCH[1]}
number=${BASH_REMATCH[2]}
[ -s "$report" ] || refuse "$report is empty: the evidence starts with what was run and seen"
grep -q 'sadara:validation' "$report" && refuse "$report already carries a validation marker; the script adds it"

head=$(gh pr view "$url" --json state,headRefOid --jq 'select(.state == "OPEN") | .headRefOid')
[ -n "$head" ] || refuse "$url is not an open pull request"

# 1. Nothing secret, no attribution.
gitleaks dir --config "$here/../.gitleaks.toml" --redact=100 --no-banner --log-level error "$report" ||
  refuse "$report carries something gitleaks calls a secret"
bash "$here/check-attribution.sh" --message-file "$report"

# 2. The screenshots, checked, then stored beside every other PR's.
images=()
if [ -n "$shots" ]; then
  [ -d "$shots" ] || refuse "$shots is not a directory"
  while IFS= read -r -d '' file; do images+=("$file"); done < <(find "$shots" -maxdepth 1 -type f -print0 | sort -z)
  [ "${#images[@]}" -gt 0 ] || refuse "$shots holds no screenshot"
  [ "${#images[@]}" -le "$MAX_IMAGES" ] || refuse "more than $MAX_IMAGES screenshots: show what proves the change"
  for file in "${images[@]}"; do
    name=$(basename "$file")
    [[ "$name" =~ ^[a-z0-9][a-z0-9-]*\.png$ ]] || refuse "$name: name screenshots [a-z0-9-]+.png"
    [ "$(head -c 8 "$file" | od -An -tx1 | tr -d ' \n')" = 89504e470d0a1a0a ] || refuse "$name is not a PNG"
    [ "$(wc -c <"$file" | tr -d ' ')" -le "$MAX_BYTES" ] || refuse "$name is larger than 5 MB"
  done
fi

folder="${repo#*/}/pr-$number/$head"
stored=''
if [ "${#images[@]}" -gt 0 ]; then
  cache=${XDG_CACHE_HOME:-$HOME/.cache}/sadara/evidence
  if [ -d "$cache/.git" ]; then
    git -C "$cache" pull -q --ff-only
  else
    mkdir -p "$(dirname "$cache")"
    git clone -q "git@github.com:$EVIDENCE_REPO.git" "$cache"
  fi
  git -C "$cache" config user.name "$(git -C "$here/.." config user.name)"
  git -C "$cache" config user.email "$(git -C "$here/.." config user.email)"
  mkdir -p "$cache/$folder"
  cp "${images[@]}" "$cache/$folder/"
  git -C "$cache" add -- "$folder"
  if ! git -C "$cache" diff --cached --quiet; then
    git -C "$cache" commit -q -m "evidence: ${repo#*/}#$number at ${head:0:7}"
    git -C "$cache" push -q origin HEAD
  fi
  stored=$(git -C "$cache" rev-parse HEAD)
fi

# 3. The comment, posted by the engineering app.
body=$(mktemp "${TMPDIR:-/tmp}/evidence.XXXXXX")
trap 'rm -f "$body"' EXIT
{
  cat "$report"
  if [ -n "$stored" ]; then
    printf '\n\n### Screenshots\n'
    for file in "${images[@]}"; do
      name=$(basename "$file")
      printf '\n**%s**\n\n![%s](https://raw.githubusercontent.com/%s/%s/%s/%s)\n' \
        "${name%.png}" "${name%.png}" "$EVIDENCE_REPO" "$stored" "$folder" "$name"
    done
    printf '\n<sub>Stored in [%s](https://github.com/%s/tree/%s/%s).</sub>\n' \
      "$EVIDENCE_REPO" "$EVIDENCE_REPO" "$stored" "$folder"
  fi
  printf '\n<sub>Validated at %s.</sub>\n<!-- sadara:validation head=%s -->\n' "$head" "$head"
} >"$body"
token=$(bash "$here/engineering-token.sh" "$repo")
GH_TOKEN="$token" gh pr comment "$url" --body-file "$body" >/dev/null
echo "evidence: posted on $url for ${head:0:7}"

# 4. The check reads it now, not at the next push.
run=$(GH_TOKEN="$token" gh run list --repo "$repo" --workflow validation.yml --commit "$head" \
  --limit 1 --json databaseId --jq '.[0].databaseId // empty')
if [ -z "$run" ]; then
  echo "validation: no run for ${head:0:7} yet; it reads the evidence when it starts"
  exit 0
fi
GH_TOKEN="$token" gh run watch "$run" --repo "$repo" >/dev/null 2>&1 || true # let a running one finish first
GH_TOKEN="$token" gh run rerun "$run" --repo "$repo"
sleep 5
if GH_TOKEN="$token" gh run watch "$run" --repo "$repo" --exit-status >/dev/null 2>&1; then
  echo "validation: passed for ${head:0:7}"
else
  refuse "the validation check still fails — read it: gh run view $run --repo $repo --log"
fi
