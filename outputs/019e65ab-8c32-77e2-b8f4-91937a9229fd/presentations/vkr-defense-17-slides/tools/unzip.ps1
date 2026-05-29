param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ArgsRest
)

Add-Type -AssemblyName System.IO.Compression.FileSystem

if ($ArgsRest.Count -lt 2) {
    Write-Error "Usage: unzip -Z1 <zip> | unzip -p <zip> <entry>"
    exit 1
}

$mode = $ArgsRest[0]

if ($mode -eq "-Z1") {
    $zipPath = $ArgsRest[1]
    $zip = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
    try {
        foreach ($entry in $zip.Entries) {
            [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
            [Console]::WriteLine($entry.FullName)
        }
    }
    finally {
        $zip.Dispose()
    }
    exit 0
}

if ($mode -eq "-p") {
    if ($ArgsRest.Count -lt 3) {
        Write-Error "Usage: unzip -p <zip> <entry>"
        exit 1
    }
    $zipPath = $ArgsRest[1]
    $entryName = $ArgsRest[2]
    $zip = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
    try {
        $entry = $zip.Entries | Where-Object { $_.FullName -eq $entryName } | Select-Object -First 1
        if (-not $entry) {
            Write-Error "Entry not found: $entryName"
            exit 1
        }
        $stream = $entry.Open()
        try {
            $stdout = [Console]::OpenStandardOutput()
            $stream.CopyTo($stdout)
            $stdout.Flush()
        }
        finally {
            $stream.Dispose()
        }
    }
    finally {
        $zip.Dispose()
    }
    exit 0
}

Write-Error "Unsupported unzip mode: $mode"
exit 1
