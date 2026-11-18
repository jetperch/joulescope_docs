# SPDX-FileCopyrightText: 2023-2026 Jetperch LLC
# SPDX-License-Identifier: Apache-2.0

<#
.SYNOPSIS
List the Joulescope USB devices known to Windows, or remove and reinstall them.

.DESCRIPTION
Windows uses the WinUSB driver for every Joulescope.  If Windows binds a
different driver, or keeps a damaged device entry, the Joulescope software
cannot find the instrument even though Device Manager shows it.  See
https://docs.joulescope.com/en/software/joulescope_ui/troubleshooting.html

Without arguments, this script lists every Joulescope device entry,
including entries for instruments that are not connected, and warns about
connected instruments that do not use WinUSB.

.PARAMETER Reinstall
Remove every Joulescope device entry, then scan for hardware changes so that
Windows reinstalls the driver for the connected instruments.  Requires
administrator rights.  If you are not an administrator, the script asks
Windows to run it as administrator in a new window.

.EXAMPLE
powershell -ExecutionPolicy Bypass -File .\joulescope_usb.ps1

.EXAMPLE
powershell -ExecutionPolicy Bypass -File .\joulescope_usb.ps1 -Reinstall
#>

param([switch]$Reinstall)

# USB product IDs for vendor ID 16D0, including the JS110 bootloader and
# JS220 updater, which the instruments use during firmware updates.
$Products = @{
    '0E88' = 'JS110'
    '0E87' = 'JS110 bootloader'
    '10BA' = 'JS220'
    '10B9' = 'JS220 updater'
    '135A' = 'JS320'
}
$Pattern = '^USB\\VID_16D0&PID_(' + ($Products.Keys -join '|') + ')(&|\\)'

function Get-Joulescope {
    # Match on the hardware ID, not the name or class: a device bound to the
    # wrong driver may have neither the Joulescope name nor the USBDevice class.
    Get-PnpDevice | Where-Object { $_.InstanceId -match $Pattern } | ForEach-Object {
        $inf = (Get-PnpDeviceProperty -InstanceId $_.InstanceId `
                -KeyName 'DEVPKEY_Device_DriverInfPath' -ErrorAction SilentlyContinue).Data
        [PSCustomObject]@{
            Model      = $Products[$_.InstanceId.Substring(17, 4).ToUpper()]
            Present    = $_.Present
            Status     = $_.Status
            Class      = $_.Class
            Name       = $_.FriendlyName
            Service    = $_.Service
            Inf        = $inf
            InstanceId = $_.InstanceId
        }
    }
}

function Show-Joulescope {
    $devices = @(Get-Joulescope)
    if ($devices.Count -eq 0) {
        Write-Host 'No Joulescope device entries found.'
        return
    }
    $devices | Sort-Object Present, Model -Descending | Format-Table -AutoSize | Out-Host
    foreach ($d in $devices) {
        if ($d.Present -and ($d.Service -ne 'WinUSB')) {
            Write-Warning ("$($d.Model) $($d.InstanceId) uses driver service " +
                "'$($d.Service)' ($($d.Inf)), not WinUSB.  Run with -Reinstall.")
        }
    }
}

if (-not $Reinstall) {
    Show-Joulescope
    return
}

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host 'Requesting administrator rights in a new window.'
    Start-Process powershell -Verb RunAs -ArgumentList @(
        '-NoProfile', '-NoExit', '-ExecutionPolicy', 'Bypass',
        '-File', "`"$PSCommandPath`"", '-Reinstall')
    return
}

Write-Host 'Before:'
Show-Joulescope
foreach ($d in @(Get-Joulescope)) {
    Write-Host "Remove $($d.Model) $($d.InstanceId)"
    pnputil /remove-device "$($d.InstanceId)"
}
Write-Host 'Scan for hardware changes'
pnputil /scan-devices
Start-Sleep -Seconds 5
Write-Host 'After:'
Show-Joulescope
