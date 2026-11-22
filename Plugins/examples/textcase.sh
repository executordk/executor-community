#!/usr/bin/env bash
# {
#   "Id": "executor-example-textcase",
#   "Name": "Text case",
#   "Description": "Change text case",
#   "Author": "Executor",
#   "Version": "1.0.0",
#   "TriggerKeywords": ["case"]
# }
#
# Example bash plugin (runs with bash.exe from Git for Windows). Only bash and
# sed, no jq. Try: case Hello World
#
# bash has no JSON parser, so this reads the one field it needs with sed. That's
# fine for small helpers; for anything bigger, Python or Node.js is easier.
# Keep LF line endings: bash fails on CRLF.

export LC_ALL=C.UTF-8 # so \uXXXX, ${s^^} and sed handle non-ASCII text

request=$(cat)

# "search":"..." (with \" and \\ inside), then undo the JSON escapes
search=$(printf '%s' "$request" | sed -n 's/.*"search":"\(\([^"\\]\|\\.\)*\)".*/\1/p')
search=${search//\\\"/\"}
search=$(printf '%b' "$search")   # \\ and \uXXXX (Executor sends non-ASCII as \uXXXX)

json() { # escape a string for JSON
  local s=${1//\\/\\\\}
  s=${s//\"/\\\"}
  printf '"%s"' "$s"
}

item() { # title subtitle score
  printf '{"title":%s,"subtitle":%s,"score":%s,"actions":[' "$(json "$1")" "$(json "$2")" "$3"
  printf '{"id":"copy-to-clipboard","name":"Copy","text":%s},' "$(json "$1")"
  printf '{"id":"executor-paste","name":"Paste into the previous window","text":%s}]}' "$(json "$1")"
}

if [ -z "$search" ]; then
  printf '{"jsonrpc":"2.0","result":{"items":[{"title":"Type some text","subtitle":"case <text>"}]},"id":"1"}'
  exit 0
fi

lower=${search,,}
upper=${search^^}
title=$(printf '%s' "$lower" | sed 's/\(^\|[^[:alnum:]]\)\([[:alpha:]]\)/\1\u\2/g')
snake=$(printf '%s' "$lower" | sed 's/[^[:alnum:]]\+/_/g; s/^_//; s/_$//')
kebab=${snake//_/-}

printf '{"jsonrpc":"2.0","result":{"items":['
item "$upper" "UPPER CASE" 50; printf ','
item "$lower" "lower case" 40; printf ','
item "$title" "Title Case" 30; printf ','
item "$snake" "snake_case" 20; printf ','
item "$kebab" "kebab-case" 10
printf ']},"id":"1"}'
