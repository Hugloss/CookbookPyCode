# Windows and WSL setup

Use these guides in order to prepare an Ubuntu WSL2 environment for the Python
cookbook. They identify which commands run in Windows PowerShell, when
Administrator is required, and which commands run inside Ubuntu.

Start with NAT networking, DNS tunneling, and Windows proxy integration. Keep
that baseline when the network checks pass; mirrored networking is an optional
alternative to test when you need its features.

| Guide | Use it for |
| --- | --- |
| [1. WSL2 and Ubuntu](wsl_1_install.md) | Normal installation, verified offline `.wsl` images and manual import recovery, shared `.wslconfig` defaults, and Linux prerequisites. |
| [2. DNS and VPN](wsl_2_dns_fix.md) | Network checks and migration from this cookbook's former static-DNS workaround to DNS tunneling. |
| [3. uv, caching, and certificates](wsl_3_uv_setup.md) | Linux uv, a maintained Bash configuration, corporate CA trust, and dependency-download checks. |
| [4. Reclaim disk space](wsl_4_disk_space.md) | Optional maintenance after deleting data: trim, stop WSL, compact its disk, and measure reclaimed Windows storage. |

The networking profile targets Windows 11 22H2 or newer and updated WSL. In
corporate networks, follow the [proxy and APT preflight](wsl_3_uv_setup.md#verify-proxy-routing-before-installing-packages)
before installing Linux packages or uv. The optional `UV_SYSTEM_CERTS` example
requires uv 0.11.0 or newer and should be enabled only when system trust is
needed. A new 200 GB virtual disk does not occupy 200 GB immediately, and
changing the default does not shrink existing disks.

Other recipes: [pyenv](pyenv.md), [AI package installation](pip.md),
[npm](npm.md), and [legacy Windows/SUSE certificate examples](ssl_fix.ipynb).
These optional paths must follow the same approved proxy and CA policy as this
guide. For Ubuntu WSL certificates, use guide 3.

## Automated documentation checks

Run `python win_setup/verify_docs.py` from the repository root to validate
local links/anchors, Markdown fences, Bash syntax, notebook JSON, and PowerShell
syntax (when PowerShell is available). GitHub Actions runs checks on Linux and
Windows. These **static** checks do not replace real corporate-network/WSL
smoke tests described in [guide 3](wsl_3_uv_setup.md#target-machine-smoke-checks-before-declaring-setup-complete).
