#!/usr/bin/env bash
set -euo pipefail

: "${GH_TOKEN:?need GH_TOKEN}"
: "${GH_OWNER:=tealigantal}"
: "${GH_REPO:=testhub}"
: "${GH_REF:=main}"

curl -sS -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ${GH_TOKEN}" \
  "https://api.github.com/repos/${GH_OWNER}/${GH_REPO}/actions/workflows/ci.yml/dispatches" \
  -d "{\"ref\":\"${GH_REF}\"}"

echo "✅ Dispatched workflow: ${GH_OWNER}/${GH_REPO}@${GH_REF}"
