#!/usr/bin/env bash
# Fallback downloader for the MIIC dataset (NTU Dataverse).
#
# The access endpoint IGNORES HTTP Range requests entirely: a request with a
# Range header (or curl -C -) gets "200 OK" with the FULL body, not "206
# Partial Content". So resume is impossible — curl -C - just loops on
# "(33) ... doesn't support byte ranges". Each file must be fetched fresh in
# one unbroken connection. There is no Content-Length, so we can't detect a
# truncated stream mid-flight; instead we download to a .part file and, since
# we know each file's exact final size, restart from zero until .part reaches
# that size, then atomically move it into place. Re-run any time.
set -uo pipefail

# Kill the entire process group (this script + xargs + every curl) on exit or
# signal, so there are no orphaned curls reparented to init when interrupted.
trap 'trap - TERM; kill -- -$$ 2>/dev/null' EXIT INT TERM

BASE="https://researchdata.ntu.edu.sg/api/access/datafile"
OUT="datasets/miic"
mkdir -p "$OUT"

# id size filename
FILES=(
  "69912 666594169 Anomaly_train.rar"
  "69908 76171335 Inpainting_train.rar"
  "69910 57307813 Anomaly_test.rar"
  "69907 29813335 Inpainting_test.rar"
)

get() {
  read -r id size name <<<"$1"
  local final="$OUT/$name" part="$OUT/$name.part" got tries=0
  # already complete?
  got=$(wc -c <"$final" 2>/dev/null | tr -d ' '); got=${got:-0}
  if (( got == size )); then echo "[OK] $name (already complete)"; return 0; fi
  while :; do
    (( tries++ ))
    # fresh full GET to .part (no Range, no -C). --max-time covers ~666MB at
    # the slow per-connection rate; bump if Anomaly_train keeps timing out.
    curl -L --fail --connect-timeout 30 --max-time 7200 \
         -o "$part" "$BASE/${id}?format=original" || true
    got=$(wc -c <"$part" 2>/dev/null | tr -d ' '); got=${got:-0}
    echo "[..] $name $((got/1024/1024))/$((size/1024/1024)) MB (attempt $tries)"
    if (( got == size )); then
      mv -f "$part" "$final"
      echo "[OK] $name ($got bytes)"
      return 0
    fi
    rm -f "$part"   # truncated/short — discard and retry from scratch
    sleep 5
    (( tries > 50 )) && { echo "[GIVEUP] $name after $tries attempts"; return 1; }
  done
}
export -f get
export BASE OUT

# One connection per file, all in parallel. Per-IP rate limiting may apply.
printf '%s\n' "${FILES[@]}" | xargs -P4 -I{} bash -c 'get "$@"' _ {}

echo "=== final state ==="
allok=1
for e in "${FILES[@]}"; do
  read -r id size name <<<"$e"
  got=$(wc -c <"$OUT/$name" 2>/dev/null | tr -d ' '); got=${got:-0}
  if [[ "$got" == "$size" ]]; then printf '%-22s OK\n' "$name"
  else printf '%-22s PARTIAL %s/%s\n' "$name" "$got" "$size"; allok=0; fi
done
[[ $allok == 1 ]] && echo "ALL COMPLETE"
