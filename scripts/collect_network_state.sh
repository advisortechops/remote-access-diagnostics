#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-logs}"
TS="$(date -u +%Y%m%d%H%M%S)"
OUT_FILE="${OUT_DIR}/network-state-${TS}.log"

mkdir -p "$OUT_DIR"

{
  echo "timestamp_utc=$(date -u --iso-8601=seconds)"
  echo
  echo "== hostname =="
  hostname
  echo
  echo "== ip addr =="
  ip addr
  echo
  echo "== routes =="
  ip route
  echo
  echo "== resolv.conf =="
  cat /etc/resolv.conf || true
} > "$OUT_FILE"

echo "Network state written to $OUT_FILE"
