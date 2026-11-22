#!/usr/bin/env python3
# {
#   "Id": "executor-example-favfolders",
#   "Name": "Favorite folders",
#   "Description": "Quick access to folders",
#   "Author": "Executor",
#   "Version": "1.0.0",
#   "TriggerKeywords": ["fav"]
# }
#
# Example plugin that stores data between runs, in the folder Executor passes
# in EXECUTOR_PLUGIN_DATA (plugins\data\<Id>). Executor doesn't create that
# folder: the plugin creates it the first time it saves something.
#
#   fav                  lists your favorite folders
#   fav proj             filters them
#   fav C:\Projects      offers to add that folder
#
# Shows custom actions ("add", "remove") with data, and follow-up actions.

import json
import os
import sys

DATA_DIR = os.environ.get("EXECUTOR_PLUGIN_DATA", "")
DATA_FILE = os.path.join(DATA_DIR, "folders.json")


def load():
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return []  # nothing saved yet


def save(folders):
    os.makedirs(DATA_DIR, exist_ok=True)  # created only when there is something to keep
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(folders, f, indent=2)


def folder_item(path):
    return {
        "title": os.path.basename(path.rstrip("\\/")) or path,
        "subtitle": path,
        "actions": [
            {"id": "open-directory", "name": "Open", "path": path},
            {"id": "copy-to-clipboard", "name": "Copy path", "text": path},
            {"id": "remove", "name": "Remove from favorites", "data": path},
        ],
    }


def query(params):
    search = params.get("search", "").strip()
    folders = load()
    items = []

    # a folder path that isn't saved yet: offer to add it
    if search and os.path.isdir(search) and search.lower() not in (f.lower() for f in folders):
        items.append({
            "title": f"Add to favorites: {search}",
            "subtitle": "Enter adds this folder",
            "score": 100,
            "actions": [{"id": "add", "name": "Add to favorites", "data": search}],
        })

    for path in folders:
        if not search or search.lower() in path.lower():
            items.append(folder_item(path))

    if not items:
        items.append({
            "title": "No favorite folders yet" if not folders else "No match",
            "subtitle": "Add one: fav C:\\Projects",
        })
    return {"items": items}


def action(params):
    action_id = params.get("id")
    path = params.get("data", "")
    folders = load()

    if action_id == "add" and path:
        if path.lower() not in (f.lower() for f in folders):
            folders.append(path)
            folders.sort(key=str.lower)
            save(folders)
        return {"actions": [{"id": "notify", "message": f"Added to favorites: {path}"}]}

    if action_id == "remove" and path:
        folders = [f for f in folders if f.lower() != path.lower()]
        save(folders)
        return {"actions": [{"id": "notify", "message": f"Removed from favorites: {path}"}]}

    return {}


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
