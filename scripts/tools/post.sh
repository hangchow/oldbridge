#!/bin/bash
# usage: post.sh 桥名 来源URL  -- moves ONLY the single file that appeared since pre.sh; never deletes anything
S="$(cd "$(dirname "$0")" && pwd)"
for i in 1 2 3 4 5; do
  new=$(comm -13 <(sort $S/tools/before.txt) <(ls -1A ~/Downloads | sort) | grep -v '\.crdownload$' | grep -v '^\.DS_Store$')
  [ -n "$new" ] && break; sleep 2
done
n=$(printf '%s\n' "$new" | grep -c .)
if [ "$n" -ne 1 ]; then echo "ABORT: expected 1 new file, found $n: $new"; exit 1; fi
src="$HOME/Downloads/$new"
mkdir -p $S/img/raw
mv -n "$src" "$S/img/raw/$new" || { echo "ABORT: mv failed"; exit 1; }
t=$(file -b "$S/img/raw/$new" | awk '{print tolower($1)}')
case $t in
  jpeg) cp "$S/img/raw/$new" "$S/img/$1.jpg";;
  png|riff|webp|gif) sips -s format jpeg "$S/img/raw/$new" --out "$S/img/$1.jpg" >/dev/null;;
  *) echo "ABORT: not an image ($t)"; exit 1;;
esac
cp -n "$S/img/$1.jpg" "/Users/sean/workspace/bridge/$1.jpg" || echo "WARN: bridge/$1.jpg exists, not overwritten"
printf '%s.jpg\t%s\n' "$1" "$2" >> $S/img/sources.tsv
file "/Users/sean/workspace/bridge/$1.jpg"
