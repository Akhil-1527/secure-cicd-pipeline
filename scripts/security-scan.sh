#!/bin/bash
# Run the security gates locally before pushing. Best-effort: installs the
# scanners on demand. Mirrors .github/workflows/security.yml.
set -uo pipefail
cd "$(dirname "$0")/.."

fail=0
section() { echo; echo "==== $1 ===="; }

section "Secret scan (secretscan)"
[ -d /tmp/secretscan ] || git clone --depth 1 https://github.com/Akhil-1527/secretscan /tmp/secretscan
python3 /tmp/secretscan/secretscan.py . --exclude .git --exclude tests || fail=1

section "SAST (bandit)"
pip show bandit >/dev/null 2>&1 || pip install -q bandit
bandit -r app -ll || fail=1

section "Dependency audit (pip-audit)"
pip show pip-audit >/dev/null 2>&1 || pip install -q pip-audit
pip-audit -r app/requirements.txt || fail=1

section "IaC scan (checkov)"
command -v checkov >/dev/null 2>&1 || pip install -q checkov
checkov -d . --quiet --compact || fail=1

echo
if [ "$fail" -eq 0 ]; then
  echo "All gates passed."
else
  echo "One or more gates failed."
  exit 1
fi
