#!/bin/bash
# 下载维基“各级文物保护单位列表”原文：$1=key 其余=区县
k=$1; shift; mkdir -p $(dirname $0)/../$k
for d in "$@"; do f="$(dirname $0)/../$k/${d}各级文物保护单位列表.txt"
  if [ -s "$f" ] && ! grep -q 'Wikimedia Error' "$f"; then continue; fi
  for i in 1 2 3 4; do curl -s -m 40 -A 'oldbridge-research/1.0 (personal project)' -o "$f" "https://zh.wikipedia.org/w/index.php?title=$(python3 -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))' "${d}各级文物保护单位列表")&action=raw"
    grep -q 'Wikimedia Error' "$f" || break; sleep 30; done
  echo "$d $(wc -c < "$f")"; sleep 4; done
