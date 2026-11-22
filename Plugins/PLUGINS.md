# Executor script plugins

A plugin is a single script file in Executor's `plugins` folder, inside the data folder. When you type one of the plugin's trigger keywords, Executor runs the script, sends it what you typed, and shows the results it returns in the list.

A plugin reads a JSON request on stdin and writes a JSON answer on stdout, so it can be written in any language. That also makes it easy to have an AI write one for you: paste this page into the chat and describe what you want.

## Using plugins

- Put the script in the `plugins` folder in Executor's data folder.
- Executor loads plugins once, at startup. Without a `plugins` folder, no plugin code runs at all. Executor doesn't watch the folder, so after adding or changing a plugin, either restart Executor or type `-p` (or a keyword with the command `$PLUGINS$`, such as `plugins`). That reloads the folder and lists your plugins. `-pf` opens the plugins folder, and offers to create it if it doesn't exist yet.
- In the plugins list, Enter starts a plugin, and right-clicking a plugin lets you enable or disable it or show its script in the folder. The right-click menu on any plugin result also has **Open Plugins Folder** and **Reload Plugins**.
- Type a trigger keyword followed by a space, e.g. `hash hello`. A trigger keyword typed alone and Enter (`hash` + Enter) adds the space for you.
- The first time a plugin runs, its first result is **Enable plugin?**. Press Enter to allow it. Executor remembers your answer in `plugins.ini` in the plugins folder.
- Enter runs the selected result's first action. With no result selected, Enter runs the first result. Right-clicking a result lists all of its actions.
- To use a different keyword, create an ordinary Executor keyword with the command `$PLUGIN <Id>$`, e.g. keyword `h` with command `$PLUGIN executor-example-hash$`. Your own keywords always take priority over a plugin's trigger keywords. Such a keyword follows its own "add to history" setting rather than the plugin's `History` option.
- Such a keyword can also give the plugin a search, like any keyword parameter. Put it in the keyword's Parameters field or after the command, e.g. `$PLUGIN executor-example-hash$ hello`. Then `h` + Enter searches for `hello`, while `h abc` still searches for `abc`. With `$P$` in the parameter, what you type is inserted: `$P$ (sha)` makes `h abc` search for `abc (sha)`.

## Plugins made by others

A plugin can do anything a program you run yourself can do: read and delete your files, send data over the internet, or start other programs. Executor can't tell a good plugin from a harmful one. Before you enable a plugin you didn't write:

- Get it from someone you trust, and read it. A script plugin is a single readable file, so you can see everything it does.
- Consider having an AI check it. Paste the script into the chat and ask, for example:

  > Check this Executor plugin for anything malicious or risky: reading or deleting files, sending data over the network, downloading and running code, obfuscated or encoded parts, or anything unrelated to what the plugin says it does.

- Check again when you update a plugin. By default Executor remembers a plugin as enabled by its file name, so a changed file with the same name stays enabled. To have Executor ask again whenever a plugin's file changes, add this to `plugins.ini`:

  ```ini
  [Settings]
  ReapproveOnChange=1
  ```

  Executor stores a SHA-256 hash of the script when you enable it. With this setting it compares the hash when plugins are loaded, and a changed plugin shows **Enable plugin?** again.
- Be extra careful with plugins that download or run other code, or that contain long encoded strings.

## How it works

- Executor starts a new process for every query (debounced while you type) and for every action. The script reads one JSON-RPC 2.0 request from **stdin**, writes one response to **stdout**, and exits.
- The timeout is 10 seconds. A new query cancels the running one, and a cancelled or timed-out script is ended together with any processes it started.
- Executor doesn't keep a plugin process running between calls. If you want to reuse data, cache it in a file (see `EXECUTOR_PLUGIN_DATA`).
- A plugin is ordinary code that runs as you. Executor asks once before it runs a new plugin for the first time.

## File types

| Extension | Runs with | Notes |
|---|---|---|
| `.py` | `py -3`, or else `python.exe` | Executor sets `PYTHONUTF8=1` |
| `.js` `.mjs` `.cjs` | `node.exe` | |
| `.ps1` | `powershell.exe -NoProfile -ExecutionPolicy Bypass` | Executor switches stdin/stdout to UTF-8 |
| `.cmd` `.bat` | `cmd.exe` with code page 65001 | Fine for simple scripts. Batch can't parse JSON, so best for helpers that ignore the search |
| `.sh` | `bash.exe` from Git for Windows | Not WSL. Save with LF line endings |

Executor looks up the interpreter on `PATH`. You can override it in the metadata (see below).

All text in both directions is UTF-8.

## Metadata

Metadata is a JSON object in the comments at the top of the file, after an optional shebang line. Use `#` comments in Python, PowerShell and bash, and `//` in JavaScript. The header ends at the first line that isn't a comment.

```python
#!/usr/bin/env python3
# {
#   "Id": "my-hash-plugin",
#   "Name": "Hash",
#   "Description": "MD5, SHA-1 and SHA-256 of the text you type",
#   "Author": "Me",
#   "Version": "1.0.0",
#   "TriggerKeywords": ["hash"],
#   "Commands": [{"Command": "file", "Description": "Hash a file"}],
#   "SettingDefinitions": [
#     {"Type": "textbox", "Value": {"Key": "algorithm", "Label": "Default algorithm", "DefaultValue": "sha256"}}
#   ],
#   "Executor": {"Interpreter": "C:\\Python312\\python.exe", "Timeout": 5000, "History": true}
# }
```

| Field | Required | Meaning |
|---|---|---|
| `Id` | yes | A unique, stable id. Executor also uses it for the settings and data folder names. |
| `Name` | yes | The name shown in Executor |
| `TriggerKeywords` | yes | Typing one of these, then a space, starts the plugin. Each keyword is one word. |
| `Description`, `Author`, `Version` | no | Shown in Executor. Keep `Description` short (a few words): Executor's window is often narrow |
| `Icon` | no | An `.ico` (or `.exe`/`.dll`) file, relative to the script or a full path |
| `Commands` | no | Sub-commands. In `hash file C:\x.txt`, `command` is `file` and `search` is `C:\x.txt`. |
| `SettingDefinitions` | no | Settings with their defaults, passed to the script as environment variables |
| `Executor` | no | Options: `Interpreter` (a path or exe name, may contain `%VARS%`), `Timeout` (ms, 500–60000) and `History` (`true` adds what was typed, e.g. `hash hello`, to Executor's history when a result runs; default `false`) |

Executor ignores fields it doesn't know.

## The query request

When you type `hash hello world`, the script receives:

```json
{"jsonrpc": "2.0", "method": "query",
 "params": {"search": "hello world", "trigger_keyword": "hash", "command": "", "raw_query": "hash hello world"},
 "id": "1"}
```

## The query response

```json
{"jsonrpc": "2.0", "id": "1",
 "result": {"items": [
   {"title": "5eb63bbbe01eeed093cb22bb8f5acdc3",
    "subtitle": "MD5 of \"hello world\"",
    "score": 100,
    "actions": [
      {"id": "copy-to-clipboard", "name": "Copy", "text": "5eb63bbbe01eeed093cb22bb8f5acdc3"},
      {"id": "executor-paste", "name": "Paste into the previous window", "text": "5eb63bbbe01eeed093cb22bb8f5acdc3"}
    ]}
 ]}}
```

- Keep titles and subtitles short: Executor's window is often narrow, and fonts can be large.
- `title` is required. `subtitle`, `score` (higher is listed first) and `icon` (as in the metadata; defaults to the plugin's icon) are optional.
- `actions` is always an array. Enter runs the first action, and right-clicking an item lists all of them by `name`.
- Each action can carry a `data` value (a string, or any JSON). Executor sends it back unchanged when the action runs.
- To show an error, return `{"jsonrpc": "2.0", "error": {"code": -32000, "message": "No network"}, "id": "1"}`. Anything the script writes to stderr is used as the error message when the output isn't valid JSON, so a Python traceback shows its last line.

## Actions

Built-in actions. Executor runs these itself, without starting the script again:

| `id` | Fields | What it does |
|---|---|---|
| `copy-to-clipboard` | `text` | Copies the text |
| `open-url` | `url` | Opens an `http`, `https`, `mailto` or `ms-settings:` link |
| `open-directory` | `path` | Opens a folder, or selects a file in Explorer |
| `notify` | `message` | Shows a toast |

Executor actions:

| `id` | Fields | What it does |
|---|---|---|
| `executor-run` | `command` | Runs it as if you had typed it in Executor: a keyword, a path or a command line |
| `executor-paste` | `text`, optional `send_enter` | Pastes the text into the window you were in before Executor |
| `executor-open-note` | `note` | Opens a note by name |
| `executor-browser` | `url`, optional `focus` (default `true`) and `connect` | Opens the page in Executor's internal browser, like a keyword with `$B$` (or `$BN$` with `"focus": false`). `"connect": true` connects the page to Executor.js, like `$BCONNECT$` |

`executor-browser` can open a web address, or a page that comes with the plugin: an `.html` file relative to the plugin's folder (or a full path), optionally with a query string, e.g. `{"id": "executor-browser", "url": "fav.html?folder=C:\\Projects", "connect": true}`. A connected page can use [Executor.js](https://www.executor.dk/internalbrowser) to follow what's typed in Executor, set the input, run commands and so on, within the permissions the user has given. `executor.getInput(true)` returns what was typed when the page opened (e.g. `fav proj`), and `executor.getQuery()` returns the plugin's search (`proj`). That way a plugin can have its own UI inside Executor.

Any other `id` is a **custom action**. Executor calls the script with the `action` method and passes the action's `id` and `data`:

```json
{"jsonrpc": "2.0", "method": "action", "params": {"id": "end-process", "data": "1234"}, "id": "2"}
```

A script with nothing more to do returns `{"jsonrpc": "2.0", "result": {}, "id": "2"}`. The response can also list follow-up built-in actions or Executor actions:

```json
{"jsonrpc": "2.0", "result": {"actions": [{"id": "notify", "message": "Process ended"}]}, "id": "2"}
```

## Environment variables

| Variable | Value |
|---|---|
| `EXECUTOR_SETTING_<KEY>` | Each setting, with the key in upper case (`EXECUTOR_SETTING_ALGORITHM`) |
| `EXECUTOR_PLUGIN_ID`, `EXECUTOR_PLUGIN_NAME` | From the metadata |
| `EXECUTOR_PLUGIN_DATA` | A folder for this plugin's cache and data (`plugins\data\<Id>`, created by the plugin when needed) |
| `EXECUTOR_PLUGINS` | The plugins folder |
| `EXECUTOR_DATA` | Executor's data folder |
| `EXECUTOR_VERSION` | Executor's version |
| `EXECUTOR` | `1`, so a script can tell it runs in Executor |

Everything Executor stores about plugins is in the plugins folder, so deleting that folder removes plugins completely:

- `plugins.ini` holds which plugins are enabled (`[Approved]`), the optional `[Settings]` `ReapproveOnChange`, and the user's setting values, in one section per plugin `Id`:

  ```ini
  [Approved]
  hash.py=3f2a...e9 (SHA-256 of the script when it was enabled)

  [my-hash-plugin]
  algorithm=md5
  ```

  Executor creates the file the first time a plugin is enabled, and reads it when plugins are loaded.
- `data\<Id>\` is the folder `EXECUTOR_PLUGIN_DATA` points to. Executor doesn't create it, so a plugin that wants a cache creates it itself (in Python: `os.makedirs(path, exist_ok=True)`).

## Keep it fast

- Python takes about 50 ms to start and PowerShell about 300 ms, before your code even runs. Keep queries light, and import heavy modules only in the code path that needs them.
- Cache slow lookups in `EXECUTOR_PLUGIN_DATA`.
- To start a program, use an `executor-run` action rather than starting it from the script.

## Writing a plugin with AI

Paste this page into the chat, then ask, for example:

> Write an Executor script plugin in Python, using only the standard library. Trigger keyword `tz`. It should show the current time in the cities I type (e.g. `tz tokyo london`). Enter copies the time, and a second action pastes it into the previous window.

### Converting a plugin from another launcher

Plugins and extensions for most other launchers work the same way at heart: they take what you type and return a list of results with actions. That usually makes it easy to have an AI convert one. Paste this page and the other plugin's source code into the chat, then ask, for example:

> Convert this launcher plugin into an Executor script plugin. Keep what it does, use the same trigger keyword, and map its actions to Executor's built-in actions where possible.

The same caution applies here: you're running code someone else wrote, so read the converted plugin (see [Plugins made by others](#plugins-made-by-others)). Plugins that only use a script and simple results convert best. Plugins that depend heavily on their launcher's own API or UI (custom views, previews, background services) may need more work or may not be possible.
