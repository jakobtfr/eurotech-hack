#!/usr/bin/env python3
"""Fast parallel downloader for the MIIC dataset (NTU Dataverse).

The Dataverse access API honors HTTP Range requests but does not return a
Content-Length, so download managers fall back to a single throttled
connection (~30 KB/s). This script splits each file into byte-range chunks
and fetches many in parallel (via curl), writing each chunk straight to its
offset in the output file, then verifies size. Throughput scales with the
worker count (~90 KB/s per connection observed), so 16 workers ≈ 1.4 MB/s.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://researchdata.ntu.edu.sg/api/access/datafile"
OUTDIR = os.path.join("datasets", "miic")

# id, size_bytes, filename  (sizes from the dataset metadata API)
FILES = [
    (69912, 666594169, "Anomaly_train.rar"),
    (69908, 76171335, "Inpainting_train.rar"),
    (69910, 57307813, "Anomaly_test.rar"),
    (69907, 29813335, "Inpainting_test.rar"),
]

CHUNK = 8 * 1024 * 1024  # 8 MiB per range request
WORKERS = 16
RETRIES = 5


def fetch_range(fid: int, fd: int, start: int, end: int) -> int:
    # curl is dramatically faster here than urllib (per-connection throttling
    # interacts badly with urllib); shell out and pwrite the bytes at offset.
    url = f"{BASE}/{fid}?format=original"
    want = end - start + 1
    last = None
    for attempt in range(RETRIES):
        try:
            p = subprocess.run(
                ["curl", "-sf", "--max-time", "300", "-r", f"{start}-{end}", url],
                capture_output=True,
            )
            if p.returncode != 0:
                raise IOError(f"curl exit {p.returncode}: {p.stderr[:200]!r}")
            data = p.stdout
            if len(data) != want:
                raise IOError(f"short read {len(data)} != {want}")
            os.pwrite(fd, data, start)  # positional write — thread-safe, no shared offset
            return len(data)
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"failed range {start}-{end} of {fid}: {last}")


def main() -> int:
    os.makedirs(OUTDIR, exist_ok=True)

    # Build one global job list across all files so the pool stays saturated.
    jobs = []  # (fid, idx, start, end)
    layout = {}  # fid -> (path, size, nchunks)
    for fid, size, name in FILES:
        path = os.path.join(OUTDIR, name)
        if os.path.exists(path) and os.path.getsize(path) == size:
            print(f"[skip] {name} already complete")
            continue
        nchunks = (size + CHUNK - 1) // CHUNK
        layout[fid] = (path, size, nchunks)
        for i in range(nchunks):
            start = i * CHUNK
            end = min(start + CHUNK - 1, size - 1)
            jobs.append((fid, i, start, end))

    if not jobs:
        print("Nothing to do.")
        return 0

    total_bytes = sum(s for _, s, _ in layout.values())
    done = 0
    t0 = time.time()
    print(f"Downloading {len(jobs)} chunks, {total_bytes/1e6:.0f} MB, {WORKERS} workers",
          flush=True)

    # Preallocate each output file so workers can pwrite at any offset.
    fds = {}
    for fid, (path, size, _) in layout.items():
        fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
        os.ftruncate(fd, size)
        fds[fid] = fd

    try:
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futs = {ex.submit(fetch_range, fid, fds[fid], s, e): (fid, idx)
                    for (fid, idx, s, e) in jobs}
            for fut in as_completed(futs):
                n = fut.result()
                done += n
                el = time.time() - t0
                spd = done / el / 1024
                pct = done / total_bytes * 100
                eta = (total_bytes - done) / (done / el) if done else 0
                print(f"{pct:5.1f}%  {done/1e6:6.0f}/{total_bytes/1e6:.0f} MB  "
                      f"{spd:7.0f} KB/s  ETA {eta:5.0f}s", flush=True)
    finally:
        for fd in fds.values():
            os.close(fd)

    # Verify final sizes.
    ok = True
    for fid, (path, size, _) in layout.items():
        got = os.path.getsize(path)
        status = "OK" if got == size else "SIZE MISMATCH"
        if got != size:
            ok = False
        print(f"[{status}] {path}  {got} bytes", flush=True)

    print(f"Done in {time.time()-t0:.0f}s")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
