#!/usr/bin/env python3
# {
#   "Id": "executor-example-hash",
#   "Name": "Hash",
#   "Description": "MD5, SHA-1 and SHA-256",
#   "Author": "Executor",
#   "Version": "1.0.0",
#   "TriggerKeywords": ["hash"]
# }
#
# Example script plugin. Only the standard library.
# Try: hash hello world

import hashlib
import json
import sys


def query(params):
    text = params.get("search", "")
    if not text:
        return {"items": [{"title": "Type some text to hash", "subtitle": "hash <text>"}]}
    items = []
    for name, score in (("md5", 30), ("sha1", 20), ("sha256", 10)):
        digest = hashlib.new(name, text.encode("utf-8")).hexdigest()
        items.append({
            "title": digest,
            "subtitle": f"{name.upper()} of \"{text}\"",
            "score": score,
            "actions": [
                {"id": "copy-to-clipboard", "name": "Copy", "text": digest},
                {"id": "executor-paste", "name": "Paste into the previous window", "text": digest},
                {"id": "executor-browser", "name": "Search the web in Executor's browser",
                 "url": "https://duckduckgo.com/?q=" + digest},
            ],
        })
    return {"items": items}


def action(params):
    return {}  # only custom actions get here; this plugin has none


def main():
    request = json.loads(sys.stdin.read())
    method = request.get("method")
    params = request.get("params", {})
    if method == "query":
        response = {"jsonrpc": "2.0", "result": query(params), "id": request.get("id")}
    elif method == "action":
        response = {"jsonrpc": "2.0", "result": action(params), "id": request.get("id")}
    else:
        response = {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"},
                    "id": request.get("id")}
    print(json.dumps(response))


if __name__ == "__main__":
    main()
