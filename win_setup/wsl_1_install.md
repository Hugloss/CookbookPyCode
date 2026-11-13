# WSL2 and Ubuntu setup for Python

[Setup index](README.md) · Next: [DNS and VPN checks](wsl_2_dns_fix.md)

This guide targets **Windows 11 22H2 or newer**, an updated WSL installation,
and Ubuntu. The examples use Ubuntu 24.04. WSL itself also supports older
Windows releases, but the DNS tunneling and proxy features in this profile
require the newer Windows version. Check your Windows version with `winver`.

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

If WSL itself needs an update but Microsoft Store access is blocked and your
organization permits a web download, use `wsl --update --web-download`. That
command updates the **WSL runtime**; it does not install an Ubuntu distribution.
Section 3 explains distro-installation recovery. A distribution must show version
`2` for this guide. Follow Microsoft's [installation guide][install] if WSL
commands are unavailable. Do not reinstall an existing distribution just to
apply these settings.

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
networkingMode=nat
dnsTunneling=true
autoProxy=true
```

| Setting | Effect |
| --- | --- |
| `defaultVhdSize=200GB` | Sets the default virtual capacity for newly created distribution disks. It does not allocate 200 GB immediately, shrink an existing disk, or reclaim deleted data. |
| `networkingMode=nat` | Uses NAT networking as the cookbook's starting point. Verify connectivity and your VPN before considering a different mode. |
| `dnsTunneling=true` | Lets WSL resolve DNS through Windows. Existing `generateResolvConf=false` settings must be removed or changed; see the next guide. |
| `autoProxy=true` | Imports Windows HTTP proxy information. It does not install certificates into Ubuntu, and PAC-only proxies may need client-specific configuration. |

Keep NAT when it works. Mirrored mode is an optional alternative for features
such as accessing Windows-hosted services from Linux at `127.0.0.1`; its
compatibility depends on the VPN and network setup. Use the
[network checks and mode comparison](wsl_2_dns_fix.md#3-if-wsl-has-no-network-or-mirrored-mode-fails-with-your-vpn)
before adopting it. Microsoft's [networking guide][networking] explains the
addressing and features of each mode.

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

For a new distro, use **PowerShell** to list the available names and first try
the supported standard installation. Elevate if Windows requests it:

```powershell
wsl --list --online
wsl --install --distribution Ubuntu-24.04
```

On success, create your normal Linux username and password when prompted. Use the
registered name `Ubuntu-24.04` in later commands if that is what you installed.

### Installation recovery ladder when the normal path fails

Do **not** unregister or overwrite a working distro. First record the failure
and check `wsl --list --verbose`: if the distro is already registered, troubleshoot
or start it rather than repeating an install against the same name. Check
`wsl --help` for the options supported by your installed WSL version, and obey
your organization's approved software and storage policies.

**Fallback A — Microsoft Store download is unavailable.** When the organization
permits Microsoft's web-download source, try:

```powershell
wsl --install --distribution Ubuntu-24.04 --web-download
```

This `--web-download` option installs the **distribution**, unlike
`wsl --update --web-download` in section 1, which updates the runtime.

**Fallback B — the default distribution storage location is unsuitable.**
When supported by your installed WSL and permitted by IT, choose a **new, empty**
local directory with sufficient space:

```powershell
wsl --install --distribution Ubuntu-24.04 --location "C:\WSL\Ubuntu-24.04"
```

The `--location` option changes the install location; it does not solve an
unreachable distribution download. If both download and location are problems,
combine supported options only after checking `wsl --help`. Avoid existing
distribution directories.

**Fallback C — last-resort manual import of an official Ubuntu root filesystem.**
Use this when supported installation paths remain unavailable (for example on a
locked-down corporate machine), or when IT explicitly requires an imported image.
Obtain an official Ubuntu WSL archive through an approved channel and verify its
provenance according to organizational policy. The manual import path is a
**recovery procedure**, not just an optional custom-location feature. Download an
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

Run the following **inside Ubuntu as your normal Linux user**. On a corporate
network, first review the [proxy and APT preflight](wsl_3_uv_setup.md#verify-proxy-routing-before-installing-packages).
If routing or DNS fails, follow the [DNS/VPN guide](wsl_2_dns_fix.md).
If DNS works but `sudo apt update` fails, troubleshoot APT's separate proxy
configuration rather than changing DNS or disabling TLS verification.

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
[networking]: https://learn.microsoft.com/en-us/windows/wsl/networking
[size]: https://github.com/microsoft/WSL/blob/master/triage/config.yml
[ubuntu]: https://documentation.ubuntu.com/wsl/latest/howto/install-ubuntu-wsl2/
[import]: https://learn.microsoft.com/en-us/windows/wsl/use-custom-distro
[filesystems]: https://learn.microsoft.com/en-us/windows/wsl/filesystems
