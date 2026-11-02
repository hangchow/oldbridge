#!/bin/bash
# $1 = prefix path (e.g. ql15/hz_ql/hzvql) $2 start $3 end
for i in $(seq $2 $3); do n=$(printf %03d $i); u="http://www.china-qiao.com/$1$n.htm"
 t=$(curl -sL -m 15 -A Mozilla/5.0 "$u" | iconv -f gb18030 -t utf-8 -c | grep -o '<title>[^<]*' | head -1 | sed 's/<title>//')
 [ -n "$t" ] && echo "$1$n.htm	$t"; sleep 0.15; done
