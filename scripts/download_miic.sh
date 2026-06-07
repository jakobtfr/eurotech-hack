#!/usr/bin/env bash
# Robust, resumable downloader for the MIIC dataset (NTU Dataverse).
#
# The access API sends NO Content-Length, so curl cannot detect a truncated
# stream: when NTU drops the connection mid-transfer, curl exits "successfully"
# with a partial file. We know each file's exact size, so we LOOP curl -C -
# (HTTP range resume from the current offset) until the file reaches that size.
# One connection per file, 4 files in parallel — gentle enough to avoid the
# per-IP rate limiting that aggressive parallelism triggers. Re-run any time.
set -uo pipefail

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
  local out="$OUT/$name" got tries=0
  got=$(wc -c <"$out" 2>/dev/null | tr -d ' '); got=${got:-0}
  while (( got < size )); do
    (( tries++ ))
    # -C - resumes from byte $got via a Range request; loop handles truncation.
    curl -L -C - --retry 5 --retry-delay 5 --retry-all-errors \
         --connect-timeout 30 --max-time 1800 \
         -o "$out" "$BASE/${id}?format=original" || true
    local new; new=$(wc -c <"$out" 2>/dev/null | tr -d ' '); new=${new:-0}
    if (( new == got )); then          # no progress this round — back off
      sleep 10
    fi
    got=$new
    echo "[..] $name $((got/1024/1024))/$((size/1024/1024)) MB (round $tries)"
    (( tries > 200 )) && { echo "[GIVEUP] $name after $tries rounds"; return 1; }
  done
  echo "[OK] $name ($got bytes)"
}
export -f get
export BASE OUT

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
