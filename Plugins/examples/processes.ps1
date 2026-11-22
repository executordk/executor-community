# {
#   "Id": "executor-example-processes",
#   "Name": "Processes",
#   "Description": "Find running processes",
#   "Author": "Executor",
#   "Version": "1.0.0",
#   "TriggerKeywords": ["proc"]
# }
#
# Example PowerShell plugin with a custom action ("end-process").
# Executor sets UTF-8 for stdin/stdout before running the script.
# Try: proc note

$request = [Console]::In.ReadToEnd() | ConvertFrom-Json
$id = $request.id

function Reply($result) {
    @{ jsonrpc = '2.0'; result = $result; id = $id } | ConvertTo-Json -Depth 6 -Compress
}

if ($request.method -eq 'query') {
    $search = $request.params.search
    $items = @(Get-Process -ErrorAction SilentlyContinue |
        Where-Object { $_.ProcessName -like "*$search*" } |
        Sort-Object ProcessName | Select-Object -First 20 | ForEach-Object {
            $actions = @()
            if ($_.Path) {
                $actions += @{ id = 'open-directory'; name = 'Open folder'; path = $_.Path }
                $actions += @{ id = 'copy-to-clipboard'; name = 'Copy path'; text = $_.Path }
            }
            $actions += @{ id = 'end-process'; name = 'End process'; data = "$($_.Id)" }
            @{
                title    = "$($_.ProcessName) ($($_.Id))"
                subtitle = $(if ($_.Path) { $_.Path } else { 'No path (system process)' })
                actions  = $actions
            }
        })
    Reply @{ items = $items }
}
elseif ($request.method -eq 'action') {
    if ($request.params.id -eq 'end-process') {
        Stop-Process -Id ([int]$request.params.data) -ErrorAction SilentlyContinue
        # Executor extension: follow-up built-in actions
        Reply @{ actions = @(@{ id = 'notify'; message = 'Process ended' }) }
    }
    else { Reply @{} }
}
