#!/usr/bin/env bash
# Resilient MIIC downloader for an endpoint that IGNORES HTTP Range.
#
# NTU's access API answers every request with "200 OK" + the full body from
# byte 0 (never "206"), and sends no Content-Length, so curl -C - can't resume
# and can't detect truncation. Two tricks make this robust anyway:
#
#   1. RESUME-BY-APPEND. The body is byte-identical every request, so we fetch
#      from 0, discard the bytes we already have (tail -c +N), and append only
#      the new tail. Progress is monotonic — a dropped connection never loses
#      ground; we just re-receive the prefix next round (bandwidth waste, but
#      guaranteed convergence as long as any round gets past the current size).
#   2. SPEED FLOOR. --speed-limit/--speed-time abort a stalled connection
#      (NTU throttles hard) so the loop reconnects instead of hanging for hours.
#
# Serial, smallest-first, so easy files finish before the 635 MB one. Resumable:
# re-run any time, it picks up from each .part's current size.
set -uo pipefail
trap 'trap - TERM; kill -- -$$ 2>/dev/null' EXIT INT TERM

BASE="https://researchdata.ntu.edu.sg/api/access/datafile"
OUT="datasets/miic"
mkdir -p "$OUT"

# id size filename  (smallest first; Inpainting_test usually already complete)
FILES=(
  "69907 29813335 Inpainting_test.rar"
  "69910 57307813 Anomaly_test.rar"
  "69908 76171335 Inpainting_train.rar"
  "69912 666594169 Anomaly_train.rar"
)

partsize() { wc -c <"$1" 2>/dev/null | tr -d ' ' || echo 0; }

get() {
  local id="$1" size="$2" name="$3"
  local final="$OUT/$name" part="$OUT/$name.part"
  local got rounds=0 stuck=0 prev=-1
  # already complete (final or part)?
  if [[ $(partsize "$final") == "$size" ]]; then echo "[OK] $name (complete)"; return 0; fi
  got=$(partsize "$part")
  while (( got < size )); do
    (( rounds++ ))
    # Full stream from 0; locally skip the $got bytes we already hold, append
    # the rest. --speed-limit 3000/--speed-time 60: abort if <3KB/s for 60s.
    curl -sL --fail --connect-timeout 30 --max-time 3600 \
         --speed-limit 3000 --speed-time 60 \
         "$BASE/${id}?format=original" \
      | tail -c "+$((got + 1))" >> "$part"
    got=$(partsize "$part")
    echo "[..] $name $((got/1048576))/$((size/1048576)) MB (round $rounds)"
    if (( got == prev )); then          # no progress this round
      (( stuck++ )); sleep $(( stuck < 6 ? stuck*10 : 60 ))
    else
      stuck=0
    fi
    prev=$got
    (( stuck > 20 )) && { echo "[GIVEUP] $name stalled at $got/$size"; return 1; }
    if (( got > size )); then echo "[ERR] $name overshot ($got>$size) — bad append, resetting"; : > "$part"; got=0; fi
  done
  mv -f "$part" "$final"
  echo "[OK] $name ($got bytes)"
}

for e in "${FILES[@]}"; do
  read -r id size name <<<"$e"
  get "$id" "$size" "$name" || echo "[WARN] $name incomplete, continuing"
done

echo "=== final state ==="
allok=1
for e in "${FILES[@]}"; do
  read -r id size name <<<"$e"
  got=$(partsize "$OUT/$name")
  if [[ "$got" == "$size" ]]; then printf '%-22s OK\n' "$name"
  else printf '%-22s PARTIAL %s/%s\n' "$name" "$got" "$size"; allok=0; fi
done
[[ $allok == 1 ]] && echo "ALL COMPLETE"
