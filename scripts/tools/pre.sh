#!/bin/bash
# snapshot Downloads before a browser download
ls -1A ~/Downloads > "$(cd "$(dirname "$0")" && pwd)"/tools/before.txt && echo snapshot ok
