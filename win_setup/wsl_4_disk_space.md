# Reclaim Windows disk space used by WSL2

[WSL setup overview](README.md) · [Install WSL](wsl_1_install.md)

Use this after deleting substantial data inside Ubuntu WSL2 while its backing
VHDX still occupies too much Windows disk space. The procedure covers a normal
dynamically expanding distro disk and reclaims unused backing storage.

## Choose the right terminal

| Task | Where to run it | Elevation |
| --- | --- | --- |
| Inspect Linux usage and trim free blocks | The selected WSL distro | `sudo` for `fstrim` |
| Inspect WSL, locate its disk, use native `--compact` | Windows PowerShell | Ordinary PowerShell |
| Run Hyper-V cmdlets or DiskPart | Windows PowerShell | **Run as Administrator** |

Use the Windows account that owns the distro. Elevating with a different
administrator's credentials changes `HKCU` and can select a different user's
registrations. Do not guess a VHDX path when discovery fails.

Before proceeding, save your work, stop databases and other jobs cleanly, and
have a recoverable backup of important data outside this VHDX. Close Docker
Desktop, WSL terminals, and IDE connections when instructed below: they can
restart WSL automatically. `wsl --shutdown` stops **all** running distros.

## 1. Select the distro and trim its root filesystem

**Ordinary Windows PowerShell:**

```powershell
$distro = "Ubuntu" # Replace with the exact name shown below.
wsl --list --verbose
wsl --version
wsl --help
```

Confirm the selected distro has **VERSION 2**. If it is missing or is WSL1,
stop and check the [installation guide](wsl_1_install.md). Note whether help
lists `--compact` under `--manage`; that determines which method to use later.

Open the selected distro:

```powershell
wsl --distribution $distro
```

**Inside that WSL distro:**

```bash
df -h /
sudo fstrim -v /
exit
```

`fstrim` discards blocks no longer used by the mounted root filesystem. The
root-specific command avoids trimming unrelated mounted filesystems. If it
fails, investigate the reported filesystem or WSL error before using the manual
compaction method. Its reported byte count is not a promised Windows saving.

## 2. Locate the backing file and record its size

**Windows PowerShell, under the distro's owning account:**

```powershell
$distro = "Ubuntu" # Use the same exact distro name as above.
$entries = @(
    Get-ChildItem -Path HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss -ErrorAction Stop |
        Where-Object { $_.GetValue("DistributionName") -eq $distro }
)
if ($entries.Count -ne 1) {
    throw "Expected one registration for '$distro'. Check the name and Windows account."
}
if ($entries[0].GetValue("Version") -ne 2) {
    throw "This guide requires a WSL2 distribution."
}
$base = $entries[0].GetValue("BasePath")
if ([string]::IsNullOrWhiteSpace($base)) {
    throw "The distro registration has no BasePath."
}
$name = $entries[0].GetValue("VhdFileName")
if ([string]::IsNullOrWhiteSpace($name)) {
    $name = "ext4.vhdx"
}
$vhd = Join-Path $base $name -ErrorAction Stop
if ([IO.Path]::GetExtension($vhd) -ne ".vhdx" -or
    -not (Test-Path -LiteralPath $vhd -PathType Leaf)) {
    throw "Expected an existing VHDX file: $vhd"
}
$vhdItem = Get-Item -LiteralPath $vhd -ErrorAction Stop
$beforeBytes = $vhdItem.Length
$vhdItem | Select-Object FullName, Attributes, @{
    Name = "FileLengthGiB"
    Expression = { [math]::Round($_.Length / 1GB, 2) }
}
```

Check the printed path. Discovery respects imported distros with a registered
`VhdFileName`; `ext4.vhdx` is the default. `FileLengthGiB` measures file length,
not necessarily allocated Windows space; see the verification section below.

## 3. Stop WSL and choose one compaction method

Close applications that can reopen WSL. In **Windows PowerShell**:

```powershell
wsl --shutdown
if ($LASTEXITCODE -ne 0) { throw "WSL shutdown failed." }
wsl --list --verbose
```

Confirm the selected distro shows **Stopped**. Keep it stopped until compaction
and any required detachment finish. Do not restart Windows, power off the
computer, or run another compaction operation while one is in progress.

### A. Preferred: native WSL compaction

**Ordinary Windows PowerShell**, in the same session used for discovery:

Use this only when your installed `wsl --help` advertises `--compact` under
`--manage`. Microsoft introduced the command in WSL 2.9.8; the stable 3.0.5
release includes further compaction fixes. Check the installed capability even
when a newer release exists.

```powershell
wsl --manage $distro --compact
if ($LASTEXITCODE -ne 0) {
    throw "Native compaction failed. Resolve the reported error before proceeding."
}
```

WSL resolves and compacts its own disk; the Hyper-V PowerShell module is not
required. A supported native command that fails is a troubleshooting case, not
a reason to try another method immediately. Use method B only when the native
option is unavailable. On success, continue to section 4.

### B. Manual compaction when native `--compact` is unavailable

Open **PowerShell as Administrator under the same Windows account**. Variables
do not carry over from the previous window: rerun sections **2 and 3** in this
elevated session, using the same distro name. Confirm it is still stopped.

#### With the Hyper-V PowerShell module

Check that all required commands exist:

```powershell
Get-Command Get-VHD, Mount-VHD, Optimize-VHD, Dismount-VHD -ErrorAction Stop |
    Out-Null
```

If commands are missing, use the DiskPart subsection below. WSL installation
does not guarantee these management cmdlets are installed; Windows Home does
not include the full Hyper-V role. Do not install Hyper-V merely to run this
recipe if the native or DiskPart method is available.

Still in **PowerShell as Administrator**:

```powershell
$vhdItem = Get-Item -LiteralPath $vhd -ErrorAction Stop
if ($vhdItem.Attributes -band [IO.FileAttributes]::SparseFile) {
    throw "This manual recipe does not handle sparse files; review WSL support first."
}
$disk = Get-VHD -Path $vhd -ErrorAction Stop
if ($disk.VhdType -ne "Dynamic" -or $disk.Attached) {
    throw "Expected a detached, dynamically expanding VHDX."
}

$mounted = $false
try {
    Mount-VHD -Path $vhd -ReadOnly -NoDriveLetter -ErrorAction Stop
    $mounted = $true
    Optimize-VHD -Path $vhd -Mode Full -ErrorAction Stop
}
finally {
    if ($mounted) {
        Dismount-VHD -Path $vhd -ErrorAction Stop
    }
}
```

The read-only attachment enables Full mode. Without it, Microsoft documents
that VHDX Full mode falls back to Prezeroed. `-ErrorAction Stop` prevents a
failed mount from silently continuing, and `finally` detaches a successful
mount even if optimization fails. Resolve any detachment error before starting
WSL; do not treat it as successful cleanup.

#### Without the Hyper-V module: DiskPart

Use this instead of the Hyper-V commands, still in **PowerShell as
Administrator**. If the file has the `SparseFile` attribute, stop and review
version-specific WSL support; do not toggle sparse mode to force this recipe.

```powershell
$vhd
diskpart
```

At the **DiskPart prompt**, replace the example with the exact path printed
above. PowerShell variables such as `$vhd` do not expand inside DiskPart:

```text
select vdisk file="C:\exact\verified\path\ext4.vhdx"
detail vdisk
```

Check that the correct disk is selected, dynamically expanding, and detached.
If selection or inspection fails, stop; do not continue with a previous disk
selection. Only after these checks, enter:

```text
compact vdisk
exit
```

DiskPart supports compaction while the dynamic disk is detached, so this method
needs no attachment or dismount. Stop on any error; do not clear filesystem
attributes or change disk type to make compaction proceed.

## 4. Measure the result and reopen the selected distro

In the same **Windows PowerShell** session used for compaction:

```powershell
$afterBytes = (Get-Item -LiteralPath $vhd -ErrorAction Stop).Length
[pscustomobject]@{
    BeforeFileLengthGiB = [math]::Round($beforeBytes / 1GB, 2)
    AfterFileLengthGiB = [math]::Round($afterBytes / 1GB, 2)
    FileLengthReductionGiB = [math]::Round(($beforeBytes - $afterBytes) / 1GB, 2)
}
```

With Hyper-V cmdlets available, **Administrator PowerShell** can also show:

```powershell
Get-VHD -Path $vhd -ErrorAction Stop | Select-Object Path, VhdType, Attached, @{
    Name = "FileSizeGiB"; Expression = { [math]::Round($_.FileSize / 1GB, 2) }
}, @{
    Name = "VirtualSizeGiB"; Expression = { [math]::Round($_.Size / 1GB, 2) }
}
```

`FileSize` describes the backing VHD file; `Size` is its virtual capacity.
For sparse or compressed files, file length can exceed actual allocation:
check **Size on disk** in Windows file properties and the drive's free space.
PowerShell's `1GB` divisor uses binary units, hence the **GiB** labels.
Successful compaction can reclaim little or nothing if no further optimization
is possible; its result is not expected to match Linux used space exactly.

After successful completion and detachment, start the intended distro:

```powershell
wsl --distribution $distro
```

Inside WSL, run `df -h /` and check your usual project files and applications.
This is a startup and usage check, not a filesystem integrity test. The Linux
filesystem may still report approximately 1 TB of capacity; that is normal.
Similarly, `.wslconfig` setting `defaultVhdSize=200GB` sets the default maximum
for **new** distro disks. It neither shrinks an existing disk nor reclaims its
allocated Windows storage.

## Sources

- [Microsoft: WSL disk space and disk location](https://learn.microsoft.com/en-us/windows/wsl/disk-space)
- [Microsoft: native compaction implementation](https://github.com/microsoft/WSL/pull/40481), [WSL 2.9.8 release](https://github.com/microsoft/WSL/releases/tag/2.9.8), and [WSL 3.0.5 release](https://github.com/microsoft/WSL/releases/tag/3.0.5)
- [Microsoft: Optimize-VHD](https://learn.microsoft.com/en-us/powershell/module/hyper-v/optimize-vhd) and [Mount-VHD](https://learn.microsoft.com/en-us/powershell/module/hyper-v/mount-vhd)
- [Microsoft: compact vdisk](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/compact-vdisk)
- [Microsoft: WSL configuration](https://learn.microsoft.com/en-us/windows/wsl/wsl-config) and [sparse file sizes](https://learn.microsoft.com/en-us/windows/win32/fileio/obtaining-the-size-of-a-sparse-file)
- [util-linux: fstrim manual](https://man7.org/linux/man-pages/man8/fstrim.8.html)
