#!/usr/bin/env python3
# {
#   "Id": "executor-example-colorpreview",
#   "Name": "Color preview",
#   "Description": "Preview and copy colors",
#   "Author": "Executor",
#   "Version": "1.0.0",
#   "TriggerKeywords": ["color"]
# }
#
# Example plugin that opens its own page in Executor's internal browser
# (the "executor-browser" action). The page, colorpreview.html, sits next to
# this script and is connected to Executor with Executor.js ("connect": true),
# so it follows what you type: keep typing colors and the preview updates.
#
# Try: color #ff8800    color 255,136,0    color rgb(0 120 215)    color teal
#
# For the live updates, put executor-1.0.0.js (from the Executor community
# repository) in the plugins folder too. Without it the page still shows the
# color, it just doesn't follow the input.

import colorsys
import json
import re
import sys

NAMED = {  # a few CSS names; enough for the example
    "black": (0, 0, 0), "white": (255, 255, 255), "red": (255, 0, 0),
    "green": (0, 128, 0), "blue": (0, 0, 255), "yellow": (255, 255, 0),
    "orange": (255, 165, 0), "purple": (128, 0, 128), "pink": (255, 192, 203),
    "gray": (128, 128, 128), "grey": (128, 128, 128), "teal": (0, 128, 128),
    "navy": (0, 0, 128), "gold": (255, 215, 0), "silver": (192, 192, 192),
}


def parse_color(text):
    """#rgb, #rrggbb, rgb(r, g, b), r,g,b or a CSS name -> (r, g, b) or None."""
    t = text.strip().lower()
    if t in NAMED:
        return NAMED[t]
    m = re.fullmatch(r"#?([0-9a-f]{3}|[0-9a-f]{6})", t)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    m = re.fullmatch(r"(?:rgb\()?\s*(\d{1,3})[\s,]+(\d{1,3})[\s,]+(\d{1,3})\s*\)?", t)
    if m and all(int(v) <= 255 for v in m.groups()):
        return tuple(int(v) for v in m.groups())
    return None


def describe(rgb):
    r, g, b = rgb
    hexs = "#{:02X}{:02X}{:02X}".format(r, g, b)
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    rgbs = f"rgb({r}, {g}, {b})"
    hsls = f"hsl({round(h * 360)}, {round(s * 100)}%, {round(l * 100)}%)"
    return hexs, rgbs, hsls


def query(params):
    search = params.get("search", "")
    rgb = parse_color(search) if search.strip() else None
    if rgb is None:
        return {"items": [{
            "title": "Type a color",
            "subtitle": "e.g. #ff8800, 255,136,0 or teal",
        }]}

    hexs, rgbs, hsls = describe(rgb)
    page = "colorpreview.html?c=" + hexs[1:]  # relative to this plugin's folder
    return {"items": [
        {
            "title": hexs,
            "subtitle": f"{rgbs}  ·  {hsls}",
            "score": 100,
            "actions": [
                # opens the page in the internal browser; "focus": false keeps
                # typing in Executor's input, which the connected page follows
                {"id": "executor-browser", "name": "Preview", "url": page,
                 "connect": True, "focus": False},
                {"id": "copy-to-clipboard", "name": "Copy " + hexs, "text": hexs},
                {"id": "copy-to-clipboard", "name": "Copy " + rgbs, "text": rgbs},
                {"id": "copy-to-clipboard", "name": "Copy " + hsls, "text": hsls},
            ],
        },
    ]}


def main():
    request = json.loads(sys.stdin.read())
    if request.get("method") == "query":
        result = query(request.get("params", {}))
    else:
        result = {}  # only built-in actions: nothing to do here
    print(json.dumps({"jsonrpc": "2.0", "result": result, "id": request.get("id")}))


if __name__ == "__main__":
    main()
