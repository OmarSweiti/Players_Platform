#!/usr/bin/env bash
# The delivery board (docs/implementation/03-github-workflow.md, "The board"):
# one GitHub Project for the three repositories, its fields, and the links to
# the repositories. Idempotent: what exists is checked against what this file
# declares, only what is missing is created, and a field that exists in another
# shape is refused, never rewritten.
#
#   ./scripts/gh-project.sh            # create what is missing, then check
#   ./scripts/gh-project.sh --check    # read-only: report drift, exit 1 on any
#
# The board holds status; the plan of record is docs/implementation/. The
# Phase and Stage options are read from the plan itself: the phase files'
# titles and the demo milestone's stages.
#
# It runs as the maintainer's own login, which needs the `project` scope
# (gh auth refresh -s project,read:project): a project on a personal account
# is out of reach of a GitHub App, the engineering app included.
#
# Not settable through GitHub's API, and so printed at the end as clicks: each
# view's grouping and sorting. The built-in workflows stay as GitHub sets them.
set -euo pipefail
cd "$(dirname "$0")/.." || exit 2

readonly OWNER=OmarSweiti
readonly TITLE='Sadara delivery'
REPOSITORIES=(Players_Platform Players_Platform_Backend Players_Platform_Frontend)
readonly MILESTONE=docs/implementation/demo-milestone.md

mode=apply
case "${1:-}" in
  '') ;;
  --check) mode=check ;;
  *) echo "usage: $0 [--check]" >&2; exit 2 ;;
esac

die() { echo "gh-project: $*" >&2; exit 1; }
say() { printf '  %-7s %s\n' "$1" "$2"; }

gh auth status 2>&1 | grep -q "'project'" ||
  die "the login lacks the 'project' scope: run gh auth refresh -s project,read:project"

# ── What the board must carry ───────────────────────────────────────────────
# Phase: "# Phase 1 — MVP (BRD release 1)" → "1 MVP".
phases=$(for file in docs/implementation/phase-[0-9]-*.md; do head -1 "$file"; done |
  sed -E 's/^# Phase ([0-9]+) — ([^(]*[^ (]).*$/\1 \2/' |
  jq -R -s 'split("\n") | map(select(length > 0) | {name: ., color: "BLUE", description: ""})')
# Stage: the demo milestone's table, "| A — Harnesses, … | `0.1.1` · … |".
stages=$(sed -n '/<!-- milestone:steps:begin -->/,/<!-- milestone:steps:end -->/p' "$MILESTONE" |
  sed -n -E 's/^\| ([A-Z] — [^|]*[^ |]) *\|.*$/\1/p' |
  jq -R -s 'split("\n") | map(select(length > 0) | {name: ., color: "PURPLE", description: ""})
    + [{name: "after the demo", color: "GRAY", description: "Not in the demo milestone"}]')
[ "$(jq length <<<"$phases")" -ge 1 ] || die "no phase file title was read"
[ "$(jq length <<<"$stages")" -ge 2 ] || die "no stage was read from $MILESTONE"

spec=$(jq -n --argjson phases "$phases" --argjson stages "$stages" '[
  {name: "Phase", dataType: "SINGLE_SELECT", options: $phases},
  {name: "Stage", dataType: "SINGLE_SELECT", options: $stages},
  {name: "Group", dataType: "TEXT"},
  {name: "Microstep", dataType: "TEXT"},
  {name: "Risk", dataType: "SINGLE_SELECT", options: [
    {name: "security", color: "RED", description: "risk: security"},
    {name: "migration", color: "ORANGE", description: "risk: migration"},
    {name: "breaking", color: "YELLOW", description: "risk: breaking"},
    {name: "none", color: "GRAY", description: "Labelled, with no risk label"}]},
  {name: "Priority", dataType: "SINGLE_SELECT", options: [
    {name: "P0", color: "RED", description: "priority: P0"},
    {name: "P1", color: "ORANGE", description: "priority: P1"},
    {name: "P2", color: "GRAY", description: "priority: P2"}]},
  {name: "Blocked", dataType: "SINGLE_SELECT", options: [
    {name: "needs answer", color: "RED", description: "needs: answer"},
    {name: "needs decision", color: "ORANGE", description: "needs: decision"},
    {name: "not blocked", color: "GREEN", description: ""}]}
]')
readonly STATUSES='["Todo","In Progress","Done"]' # GitHub's own Status field
# The views: their name, layout, filter and columns are set here; their grouping is a click (`group`).
views=$(jq -n '[
  {name: "Board — now", layout: "BOARD_LAYOUT", filter: "-status:Done", group: null,
   fields: ["Title", "Repository", "Microstep", "Risk", "Blocked"]},
  {name: "Demo build order", layout: "TABLE_LAYOUT", filter: "", group: "Stage",
   fields: ["Title", "Status", "Repository", "Microstep", "Stage", "Risk"]},
  {name: "Phase plan", layout: "TABLE_LAYOUT", filter: "", group: "Phase",
   fields: ["Title", "Status", "Repository", "Phase", "Group", "Microstep"]},
  {name: "Blocked", layout: "TABLE_LAYOUT", filter: "blocked:\"needs answer\",\"needs decision\"", group: null,
   fields: ["Title", "Status", "Repository", "Microstep", "Blocked", "Priority"]}
]')

readonly DESCRIPTION='Delivery board for Sadara. docs/implementation/ is the plan of record; this board holds status: what is in flight, what merged, what is blocked.'
IFS= read -r -d '' readme <<'MD' || true # not $(cat …): bash 3.2 misparses a quote in it
**The plan of record is [`docs/implementation/`](https://github.com/OmarSweiti/Players_Platform/tree/development/docs/implementation)**; this board holds status. When the board and [`progress.md`](https://github.com/OmarSweiti/Players_Platform/blob/development/docs/implementation/progress.md) disagree, the board is stale.

**Cards.** Every pull request into `development`, in the three repositories: `just pr` files it as *In Progress*, `just merge` moves it to *Done*, and `just gh-project-sync` catches up whatever was opened or merged elsewhere (Dependabot's, merged in the browser). One issue per microstep, in the umbrella, opened when the step starts (`just step-issue N.N.N`) and closed by the umbrella pull request that records the step done.

**Fields.** *Phase*, *Stage* (the demo milestone's build order), *Group* and *Microstep* come from the title's step; *Risk*, *Priority* and *Blocked* from the labels. The scripts set them; edit a label, not a card.
MD
readme=${readme%$'\n'}

# ── Read the board ──────────────────────────────────────────────────────────
read_board() { # read_board <number> — the project, its fields and its linked repositories
  gh api graphql -F owner="$OWNER" -F number="$1" -f query='
    query($owner: String!, $number: Int!) {
      user(login: $owner) { projectV2(number: $number) {
        id number url title public shortDescription readme
        fields(first: 50) { nodes {
          ... on ProjectV2FieldCommon { id name dataType }
          ... on ProjectV2SingleSelectField { options { name } } } }
        repositories(first: 20) { nodes { nameWithOwner } }
        views(first: 20) { nodes {
          id name layout filter
          fields(first: 30) { nodes { ... on ProjectV2FieldCommon { name } } }
          groupByFields(first: 3) { nodes { ... on ProjectV2FieldCommon { name } } } } } } } }' \
    --jq '.data.user.projectV2'
}

matches=$(gh project list --owner "$OWNER" --closed --limit 200 --format json |
  jq -r --arg title "$TITLE" '[.projects[] | select(.title == $title) | .number] | map(tostring) | join(" ")')
case "$matches" in
  *' '*) die "more than one project is named '$TITLE' ($matches): resolve it by hand" ;;
  '')
    [ "$mode" = apply ] || die "no project named '$TITLE': run without --check to create it"
    number=$(gh project create --owner "$OWNER" --title "$TITLE" --format json | jq -r .number)
    [[ "$number" =~ ^[0-9]+$ ]] || die "GitHub returned no project number"
    echo "created project #$number" ;;
  *) number=$matches ;;
esac
board=$(read_board "$number")
project_id=$(jq -r .id <<<"$board")
echo "board: $(jq -r .url <<<"$board")"

# ── Apply what is missing ───────────────────────────────────────────────────
if [ "$mode" = apply ]; then
  if [ "$(jq -r '.shortDescription // ""' <<<"$board")" != "$DESCRIPTION" ] ||
    [ "$(jq -r '.readme // ""' <<<"$board")" != "$readme" ]; then
    gh api graphql -F id="$project_id" -f description="$DESCRIPTION" -f readme="$readme" -f query='
      mutation($id: ID!, $description: String!, $readme: String!) {
        updateProjectV2(input: {projectId: $id, shortDescription: $description, readme: $readme, public: false}) {
          projectV2 { id } } }' >/dev/null
    echo "  set     description and readme"
  fi
  for index in $(jq -r 'keys[]' <<<"$spec"); do
    field=$(jq -c ".[$index]" <<<"$spec")
    name=$(jq -r .name <<<"$field")
    jq -e --arg name "$name" '.fields.nodes | any(.name == $name)' <<<"$board" >/dev/null && continue
    jq -n --arg project "$project_id" --argjson field "$field" '{
      query: "mutation($input: CreateProjectV2FieldInput!) { createProjectV2Field(input: $input) { projectV2Field { ... on ProjectV2FieldCommon { id } } } }",
      variables: {input: ({projectId: $project, dataType: $field.dataType, name: $field.name}
        + if $field.options then {singleSelectOptions: $field.options} else {} end)}}' |
      gh api graphql --input - >/dev/null
    say created "field $name"
  done
  for repository in "${REPOSITORIES[@]}"; do
    jq -e --arg repo "$OWNER/$repository" '.repositories.nodes | any(.nameWithOwner == $repo)' <<<"$board" >/dev/null &&
      continue
    repository_id=$(gh api "repos/$OWNER/$repository" --jq .node_id)
    gh api graphql -F project="$project_id" -F repository="$repository_id" -f query='
      mutation($project: ID!, $repository: ID!) {
        linkProjectV2ToRepository(input: {projectId: $project, repositoryId: $repository}) { repository { id } } }' >/dev/null
    say linked "$OWNER/$repository"
  done
  for index in $(jq -r 'keys[]' <<<"$views"); do
    view=$(jq -c ".[$index]" <<<"$views")
    name=$(jq -r .name <<<"$view")
    jq -e --arg name "$name" '.views.nodes | any(.name == $name)' <<<"$board" >/dev/null && continue
    columns=$(jq -c --argjson view "$view" '[$view.fields[] as $name | .fields.nodes[] | select(.name == $name) | .id]' <<<"$board")
    # A new project's one view, "View 1", becomes the first; the rest are created.
    view_id=$(jq -r 'first(.views.nodes[] | select(.name == "View 1") | .id) // empty' <<<"$board")
    if [ -z "$view_id" ]; then
      view_id=$(jq -n --arg project "$project_id" --argjson view "$view" --argjson columns "$columns" '{
        query: "mutation($input: CreateProjectV2ViewInput!) { createProjectV2View(input: $input) { projectV2View { id } } }",
        variables: {input: {projectId: $project, name: $view.name, layout: $view.layout,
          configuration: {visibleFieldIds: $columns}}}}' |
        gh api graphql --input - --jq .data.createProjectV2View.projectV2View.id)
    fi
    jq -n --arg id "$view_id" --argjson view "$view" --argjson columns "$columns" '{
      query: "mutation($input: UpdateProjectV2ViewInput!) { updateProjectV2View(input: $input) { projectV2View { id } } }",
      variables: {input: {viewId: $id, name: $view.name, layout: $view.layout, filter: $view.filter,
        configuration: {visibleFieldIds: $columns}}}}' |
      gh api graphql --input - >/dev/null
    say created "view $name"
    board=$(read_board "$number")
  done
  board=$(read_board "$number")
fi

# ── Check: the board as declared ────────────────────────────────────────────
drift=0
check() { # check <label> <jq expression over the board that must be true> [jq arguments…]
  local label=$1 expression=$2
  shift 2
  if jq -e "$@" "$expression" <<<"$board" >/dev/null; then say ok "$label"; else say DRIFT "$label"; drift=1; fi
}
check "private" '.public | not'
check "description and readme" '.shortDescription == $description and .readme == $readme' \
  --arg description "$DESCRIPTION" --arg readme "$readme"
check "Status: Todo · In Progress · Done" \
  '[.fields.nodes[] | select(.name == "Status") | .options | map(.name)] == [$statuses]' --argjson statuses "$STATUSES"
for index in $(jq -r 'keys[]' <<<"$spec"); do
  field=$(jq -c ".[$index]" <<<"$spec")
  check "$(jq -r '.name + ": " + (if .options then (.options | map(.name) | join(" · ")) else .dataType end)' <<<"$field")" \
    '[.fields.nodes[] | select(.name == $field.name)]
      | length == 1 and .[0].dataType == $field.dataType
        and ((.[0].options // []) | map(.name)) == (($field.options // []) | map(.name))' --argjson field "$field"
done
for repository in "${REPOSITORIES[@]}"; do
  check "linked to $OWNER/$repository" '.repositories.nodes | any(.nameWithOwner == $repository)' \
    --arg repository "$OWNER/$repository"
done
for index in $(jq -r 'keys[]' <<<"$views"); do
  view=$(jq -c ".[$index]" <<<"$views")
  check "view $(jq -r '.name + " — " + (.layout | ascii_downcase | sub("_layout"; "")) + (if .filter != "" then ", " + .filter else "" end)' <<<"$view")" \
    '[.views.nodes[] | select(.name == $view.name)] | length == 1
      and .[0].layout == $view.layout and (.[0].filter // "") == $view.filter
      and ([.[0].fields.nodes[].name] | sort) == ($view.fields | sort)' --argjson view "$view" # GitHub orders the columns itself
done

# Grouping has no API, so it is reported, never counted as drift.
clicks=$(jq -r --argjson views "$views" '.views.nodes as $live | $views[] | select(.group) | . as $view
  | select([$live[] | select(.name == $view.name) | .groupByFields.nodes[].name] != [$view.group])
  | "  click   \($view.name): ⋯ → Group by → \($view.group)"' <<<"$board")
[ -z "$clicks" ] || printf '%s\n' "$clicks"

if [ "$drift" -ne 0 ]; then
  echo
  echo "gh-project: DRIFT — what exists in another shape is never rewritten here; correct it on the board by hand, then run again" >&2
  exit 1
fi
echo
echo "no drift"
[ -n "$clicks" ] && echo "(the grouping above is a click on $(jq -r .url <<<"$board"): GitHub's API cannot set it)"
exit 0
