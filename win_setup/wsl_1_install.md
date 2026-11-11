# WSL2 and Ubuntu setup for Python

[Setup index](README.md) · Next: [DNS and VPN checks](wsl_2_dns_fix.md)

This guide targets **Windows 11 22H2 or newer**, an updated WSL installation,
and Ubuntu. The examples use Ubuntu 24.04. WSL itself also supports older
Windows releases, but the mirrored networking profile below requires the newer
Windows version. Check your Windows version with `winver`.

## 1. Install or update WSL

For a first installation, open **PowerShell as Administrator**:

```powershell
wsl --install --no-distribution
```

Restart Windows if requested. This installs WSL first so you can configure the
default disk capacity before creating a distribution.

For an existing installation, update WSL from **Windows PowerShell**; accept
elevation if Windows requests it:

```powershell
wsl --update
wsl --version
wsl --status
wsl --list --verbose
```

If Microsoft Store access is unavailable and your organization permits a web
download, use `wsl --update --web-download`. A distribution must show version
`2` in the list for this guide. Follow Microsoft's [installation guide][install]
if WSL commands are unavailable. Do not reinstall an existing distribution just
to apply the settings below.

## 2. Configure WSL2 on Windows

Use **ordinary PowerShell under the Windows account that owns your WSL
distributions**. Editing this file does not require Administrator:

```powershell
notepad "$env:USERPROFILE\.wslconfig"
```

Save the filename as `.wslconfig`, without a `.txt` extension. If it already
exists, keep a copy before editing, preserve unrelated settings, and merge these
keys into its existing `[wsl2]` section. Use only one such section.

```ini
[wsl2]
defaultVhdSize=200GB
networkingMode=mirrored
dnsTunneling=true
autoProxy=true
```

| Setting | Effect |
| --- | --- |
| `defaultVhdSize=200GB` | Sets the default virtual capacity for newly created distribution disks. It does not allocate 200 GB immediately, shrink an existing disk, or reclaim deleted data. |
| `networkingMode=mirrored` | Enables mirrored networking, including Windows/WSL IPv4 localhost connectivity. VPN compatibility still depends on the VPN and firewall. |
| `dnsTunneling=true` | Lets WSL resolve DNS through Windows. Existing `generateResolvConf=false` settings must be removed or changed; see the next guide. |
| `autoProxy=true` | Imports Windows HTTP proxy information. It does not install certificates into Ubuntu, and PAC-only proxies may need client-specific configuration. |

The file applies to **all WSL2 distributions for this Windows user**. The 200 GB
value is a per-disk creation default, not a combined Windows disk-space quota.
An existing disk can still show approximately 1 TB inside Linux after this edit.
Use [disk reclamation](wsl_4_disk_space.md) for deleted data; do not try to shrink
an existing filesystem by changing this setting. See Microsoft's
[configuration reference][config] and [new-versus-existing disk guidance][size].

Save work and close WSL terminals, WSL-connected editors, Docker Desktop, and
other applications that could restart WSL. In **PowerShell**:

```powershell
wsl --shutdown
wsl --list --verbose
```

`--shutdown` stops **all** running WSL distributions. If WSL reports an unknown
configuration key on the next start, update WSL and check the spelling instead
of assuming the setting was applied.

## 3. Install or start Ubuntu

For an existing distro, use its exact name from `wsl --list --verbose`:

```powershell
wsl --distribution Ubuntu
```

For a new distro, use **PowerShell** to list the available names and install the
chosen version. Elevate if Windows requests it:

```powershell
wsl --list --online
wsl --install --distribution Ubuntu-24.04
```

Create your normal Linux username and password when prompted. Use the registered
name `Ubuntu-24.04` in later commands if that is what you installed. If the store
download fails, Microsoft's installation guide documents the
`--web-download` alternative.

### Optional: import an Ubuntu filesystem manually

Use this only when you need an import or a custom storage location. Download an
official Ubuntu WSL root filesystem archive for your CPU architecture from
[Ubuntu's WSL instructions][ubuntu]. The input to `--import` is a filesystem tar
archive, possibly compressed, not an Ubuntu installer ISO. Use the actual
downloaded filename and a new distribution name/location:

```powershell
wsl --import Ubuntu-24.04-Manual "C:\WSL\Ubuntu-24.04-Manual" "C:\Users\YOUR_USER\Downloads\ubuntu-rootfs.tar.gz" --version 2
wsl --distribution Ubuntu-24.04-Manual
```

Imported distributions may start as `root` without creating a normal user. If
so, run these commands **inside the imported Ubuntu root shell**, replacing
`devuser` with your chosen username. If that user already exists, skip `adduser`.

```bash
apt update
apt install -y sudo nano
adduser devuser
usermod -aG sudo devuser
nano /etc/wsl.conf
```

Merge this section into `/etc/wsl.conf`; preserve existing sections:

```ini
[user]
default=devuser
```

Exit Ubuntu, then use **PowerShell** to restart only this distro:

```powershell
wsl --terminate Ubuntu-24.04-Manual
wsl --distribution Ubuntu-24.04-Manual
```

Inside Ubuntu, `whoami` should now show your normal user. Microsoft documents the
[import and default-user procedure][import].

## 4. Prepare Ubuntu for Python development

Run the following **inside Ubuntu as your normal Linux user**. If downloads
fail, complete the [DNS/VPN guide](wsl_2_dns_fix.md) before retrying.

```bash
sudo apt update
sudo apt install -y ca-certificates curl git nano build-essential python3 python3-venv
mkdir -p ~/src
cd ~/src
```

Keep Linux projects under `~/src`, with their environments and caches on the
Linux filesystem. Microsoft's [filesystem guidance][filesystems] explains why
this performs better for Linux tools than a checkout under `/mnt/c`.

If you build CPython or native extensions from source, install the libraries
required by that project. A typical optional development set is:

```bash
sudo apt install -y \
  libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev \
  wget llvm libncurses-dev xz-utils tk-dev libxml2-dev libffi-dev \
  liblzma-dev libxmlsec1-dev libcurl4-openssl-dev rsync zip gdb ninja-build
```

Continue with [DNS and VPN checks](wsl_2_dns_fix.md), then
[uv, caching, and certificates](wsl_3_uv_setup.md). Use
[disk reclamation](wsl_4_disk_space.md) only when you need to recover Windows
storage after deleting Linux data.

[install]: https://learn.microsoft.com/en-us/windows/wsl/install
[config]: https://learn.microsoft.com/en-us/windows/wsl/wsl-config
[size]: https://github.com/microsoft/WSL/blob/master/triage/config.yml
[ubuntu]: https://documentation.ubuntu.com/wsl/latest/howto/install-ubuntu-wsl2/
[import]: https://learn.microsoft.com/en-us/windows/wsl/use-custom-distro
[filesystems]: https://learn.microsoft.com/en-us/windows/wsl/filesystems
