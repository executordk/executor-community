:: {
::   "Id": "executor-example-localip",
::   "Name": "Local IP",
::   "Description": "This PC's IPv4 addresses",
::   "Author": "Executor",
::   "Version": "1.0.0",
::   "TriggerKeywords": ["localip"]
:: }
::
:: Example .cmd plugin. Try: localip
::
:: Batch files can't parse JSON, so this one ignores the request and always
:: lists the addresses (it only uses built-in actions, so Executor never calls
:: it with "action"). That suits small helpers that don't need the search;
:: for anything more, use PowerShell, Python or Node.js.

@echo off
setlocal EnableDelayedExpansion

set "items="
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
  set "ip=%%a"
  set "ip=!ip: =!"
  set "ip=!ip:(Preferred)=!"
  set "item={"title":"!ip!","subtitle":"IPv4 address","actions":[{"id":"copy-to-clipboard","name":"Copy","text":"!ip!"},{"id":"executor-paste","name":"Paste into the previous window","text":"!ip!"}]}"
  if defined items (set "items=!items!,!item!") else (set "items=!item!")
)

if not defined items set "items={"title":"No IPv4 address found","subtitle":"Not connected?"}"

echo {"jsonrpc":"2.0","result":{"items":[!items!]},"id":"1"}
