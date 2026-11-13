# Python and uv inside WSL

Use this guide after [installing WSL](wsl_1_install.md) and checking the
[network configuration](wsl_2_dns_fix.md). All commands below run **inside Ubuntu
in WSL**, as your normal Linux user; only commands marked `sudo` need Linux root.
For the full sequence, see the [Windows setup index](README.md).

## Verify proxy routing before installing packages

This step comes **before** the uv installer and, if APT cannot access its
repositories, before the `sudo apt` commands in the installation guide.

On Windows, set `autoProxy=true` in the owning user's `.wslconfig` and save it.
After stopping WSL-connected applications, use **Windows PowerShell** to run
`wsl --shutdown` and reopen Ubuntu. A normal WSL restart is necessary for
configuration changes to take effect; keep the working NAT/DNS-tunneling profile
if your VPN needs it.

Inside Ubuntu, check which proxy settings are present **without revealing their
values**, which may contain usernames, passwords, or internal addresses:

```bash
for name in HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY \
    http_proxy https_proxy all_proxy no_proxy WSL_PAC_URL; do
    if printenv "$name" >/dev/null 2>&1; then
        printf '%s: present\n' "$name"
    else
        printf '%s: absent\n' "$name"
    fi
done
```

`autoProxy=true` can import Windows' explicit HTTP/HTTPS proxy configuration.
uv recognizes `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, and `NO_PROXY` (and
their lowercase forms). If Windows uses **only a PAC file**, WSL may provide
`WSL_PAC_URL`, but standard Linux tools do not interpret that PAC file
automatically. Ask IT for an approved explicit proxy, package mirror, or
supported PAC-aware Linux solution. Do not assume installing a CA fixes routing.
It is also valid for all proxy variables to be absent if direct connectivity is
allowed.

When `curl` is installed, test actual HTTPS routing and certificate validation
against an **approved** endpoint. Replace this public PyPI URL with your approved
internal package index if direct public access is restricted:

```bash
curl --fail --show-error --location --max-time 20 \
    https://pypi.org/simple/requests/ -o /dev/null
```

If `curl` is not yet installed, configure APT below, install the approved
`curl` package, and then run this test. A successful proxy-variable check only
shows configuration presence; the HTTPS request checks connectivity and curl's
certificate trust. Never paste raw proxy-variable values, authenticated URLs,
`curl --verbose` output, or secrets into GitHub issues or CI logs.

### When APT needs its own proxy or internal mirror

`sudo` may not preserve the user's proxy environment, and APT has its own
`Acquire::http::Proxy` and `Acquire::https::Proxy` settings. If
`sudo apt update` fails while ordinary user-level HTTPS works, confirm that the
APT repository URLs and network access are approved by IT. If you are in an
imported distro's `root` shell without `sudo`, use the
[root-first-boot APT procedure](wsl_1_install.md#3-install-or-start-ubuntu)
instead of `sudoedit`. Prefer an
organization-provided Ubuntu mirror when available.

Only when an **explicit, unauthenticated proxy** is required for APT, create or
edit a root-owned configuration file with `sudoedit`:

```bash
sudoedit /etc/apt/apt.conf.d/90corporate-proxy
```

Place the following APT configuration in that file, replacing the placeholder
with the approved host and port. The URL is a proxy address, **not** the Ubuntu
repository URL. Many HTTP CONNECT proxies use the `http://` scheme even when
accessing HTTPS repositories:

```text
Acquire::http::Proxy "http://proxy.example.invalid:8080/";
Acquire::https::Proxy "http://proxy.example.invalid:8080/";
```

Do not store proxy credentials in this file, in `.bashrc`, or in a URL committed
to Git. For authenticated APT proxies, use IT-managed configuration or APT's
restricted-permission `/etc/apt/auth.conf` mechanism; do not copy credentials
into a world-readable `apt.conf.d` file. If an internal repository has custom
trust requirements, use only IT-approved CA certificates. Do not disable
repository-signature or TLS verification.

Then retry the package-index update from inside Ubuntu:

```bash
sudo apt update
```

If it still fails, inspect the approved APT sources and proxy configuration
with IT; do not automatically switch to a public mirror. APT proxy settings
are independent of uv's and curl's settings.

References: [Microsoft WSL proxy behavior](https://learn.microsoft.com/en-us/windows/wsl/troubleshooting#considerations-when-using-autoproxy-for-httpproxy-mirroring-in-wsl),
[uv environment variables](https://docs.astral.sh/uv/reference/environment/),
[Ubuntu 24.04 APT proxy transport](https://manpages.ubuntu.com/manpages/noble/man1/apt-transport-http.1.html),
and [APT credential storage](https://manpages.ubuntu.com/manpages/noble/man5/apt_auth.conf.5.html).

## Install an approved corporate CA before HTTPS downloads

If TLS is intercepted by your organization, obtain its approved **CA
certificate** via an authenticated IT channel and verify its provenance. The
certificate must be a PEM-format `.crt` file. If `ca-certificates` is not yet
installed, obtain it through the approved APT/mirror setup first; if that
bootstrap itself fails on CA trust, request an IT-provisioned image or approved
offline bootstrap instead of bypassing verification.

Install the CA in **Ubuntu**, not only in Windows:

```bash
sudo install -m 0644 /path/to/approved-company-ca.crt \
    /usr/local/share/ca-certificates/company-ca.crt
sudo update-ca-certificates
```

Replace the example path with your verified certificate. If the organization
does not intercept TLS or require a custom trust root, skip this step.
Installing a CA does not fix missing routes, PAC resolution, or proxy
authentication. Never bypass TLS certificate verification to make downloads
work. See [Ubuntu's CA installation guide](https://ubuntu.com/server/docs/how-to/security/install-a-root-ca-certificate-in-the-trust-store/).

## Install the Linux version of uv

Use a current uv release, **0.11.0 or newer** for the certificate setting below.
If a project pins an older version, follow its toolchain policy before upgrading.
`UV_SYSTEM_CERTS` was introduced in 0.11.0; `UV_NATIVE_TLS` is now deprecated.
See [Astral's environment reference](https://docs.astral.sh/uv/reference/environment/#uv_system_certs).

Install prerequisites if missing:

```bash
sudo apt update
sudo apt install -y ca-certificates curl python3
```

Before downloading the installer, complete the
[proxy/HTTPS checks](#verify-proxy-routing-before-installing-packages) and,
only when corporate TLS interception requires it, the
[Ubuntu CA installation](#install-an-approved-corporate-ca-before-https-downloads).
WSL proxy forwarding does not install certificates in Ubuntu.

For a new installation, run the [official Linux installer](https://docs.astral.sh/uv/getting-started/installation/):

```bash
(
    set -eu
    wsl_uv_installer=$(mktemp)
    trap 'rm -f "$wsl_uv_installer"' EXIT
    curl --fail --show-error --location --max-time 60 \
        https://astral.sh/uv/install.sh -o "$wsl_uv_installer"
    sh "$wsl_uv_installer"
)
```

Open a new WSL terminal, then check:

```bash
command -v uv
uv --version
uv cache dir
```

Use Linux `uv`, not `uv.exe` from a Windows installation. If uv was installed with
the standalone installer, `uv self update` updates it; otherwise use the original
package manager or your organization's approved installation method.

## Keep repositories, environments, and cache together

Keep Linux development checkouts under a directory such as `~/src`, with each
project's `.venv` beside its source. Keep uv's cache on that same Linux filesystem.
Microsoft recommends the [Linux filesystem for Linux tools](https://learn.microsoft.com/en-us/windows/wsl/filesystems).
Astral recommends [the same filesystem for cache and environment](https://docs.astral.sh/uv/concepts/cache/#cache-directory)
so installation can link files instead of copying them across filesystems.

Edit `~/.bashrc` and maintain **one** block; do not repeatedly append it:

```bash
# WSL Python tooling: keep the cache on the Linux filesystem.
export UV_CACHE_DIR="$HOME/.cache/uv"
```

The explicit cache path is usually already uv's Linux default. Leave
`UV_LINK_MODE` unset for normal operation.

**Only when uv must trust an approved corporate CA installed in Ubuntu**, add
the following *separate, conditional* line to that maintained block (uv >=
0.11.0):

```bash
export UV_SYSTEM_CERTS=true
```

Otherwise leave `UV_SYSTEM_CERTS` unset and use uv's default bundled Mozilla
roots. System certificates affect uv's TLS verification; they do not configure
proxy routing. To test without persisting this choice, prefix an actual uv
download command with `UV_SYSTEM_CERTS=true`. For an older pinned uv, follow
that version's supported certificate configuration instead.

If a particular environment cannot use links, select copying for that command.
For example, in a project that already has `pyproject.toml` and `uv.lock`:

```bash
uv sync --locked --link-mode copy
```

Copying is a compatibility choice that can use more disk space and take longer;
it is not a general WSL speed improvement. See [uv link modes](https://docs.astral.sh/uv/reference/settings/#link-mode).

This cookbook is a collection of examples without a root uv project. Do not run
`uv sync` at its root; use each example's dependency instructions. The standalone
verification below works without a project or lockfile.

`.bashrc` configures interactive Bash shells. Services, CI, other shells, and IDE
processes started elsewhere need their own environment configuration.

## Optional: explicit certificate bundles

When necessary, the approved corporate CA has already been installed in Ubuntu
before the uv installer. Certificate-bundle overrides are **not** a substitute
for fixing DNS, proxy routing, or authentication.

If your Python/Requests or curl environment needs an explicit Ubuntu bundle, add
the relevant lines to your maintained shell block:

```bash
export SSL_CERT_FILE="/etc/ssl/certs/ca-certificates.crt"
export REQUESTS_CA_BUNDLE="/etc/ssl/certs/ca-certificates.crt"
export CURL_CA_BUNDLE="/etc/ssl/certs/ca-certificates.crt"
```

These settings are optional and Ubuntu-specific:

- `SSL_CERT_FILE` selects an explicit bundle for clients that support it. In uv,
  this **overrides the default certificate source entirely**; it does not add a
  certificate to the default source. A missing or empty bundle breaks trust.
- `REQUESTS_CA_BUNDLE` makes Requests use this bundle instead of its usual
  certificate selection. Requests also uses `CURL_CA_BUNDLE` as a fallback.
- `CURL_CA_BUNDLE` selects curl's bundle. Ubuntu's curl often already uses the
  system bundle, so an explicit override may be unnecessary.

Check that the bundle exists before enabling these overrides:

```bash
test -s /etc/ssl/certs/ca-certificates.crt
```

Sources: [uv certificates](https://docs.astral.sh/uv/concepts/authentication/certificates/),
[Requests certificate verification](https://requests.readthedocs.io/en/latest/user/advanced/#ssl-cert-verification),
and [curl certificate selection](https://curl.se/docs/sslcerts.html).

## Apply changes and remove stale exports

Delete superseded exports from `.bashrc`, including `UV_NATIVE_TLS` and any
unwanted global `UV_LINK_MODE=copy`. Remove `UV_SYSTEM_CERTS=true` too when the
approved corporate CA is no longer required. Editing a file does not remove
variables already inherited by a running process. After editing, unset only
settings you intentionally retired, for example:

```bash
unset UV_NATIVE_TLS UV_LINK_MODE
# If you removed the optional system-trust setting, also run:
# unset UV_SYSTEM_CERTS
# If you removed the optional bundle overrides, also run:
# unset SSL_CERT_FILE REQUESTS_CA_BUNDLE CURL_CA_BUNDLE
source ~/.bashrc
```

Alternatively, close the old Windows terminal application and open a fresh WSL
terminal. Restart IDE processes that inherited the old values as needed.

```bash
printf 'UV_CACHE_DIR=%s\n' "${UV_CACHE_DIR:-<default>}"
printf 'UV_SYSTEM_CERTS=%s\n' "${UV_SYSTEM_CERTS:-<unset>}"
printf 'UV_LINK_MODE=%s\n' "${UV_LINK_MODE:-<default>}"
uv cache dir
```

## Verify curl, uv downloads, and Requests separately

Use an approved HTTPS endpoint and package index. In a restricted corporate
network, replace the public probe URL below and configure uv's approved index
through its normal [index configuration](https://docs.astral.sh/uv/concepts/indexes/)
before running. Keep credentials out of committed shell files and diagnostic output.

Run this block from WSL. It stops on failure. curl has a 20-second limit; the
separate uv/Requests check has a 120-second limit with a five-second kill grace.
The temporary uv environment downloads Requests through uv and then verifies an
HTTPS request through Requests. `--no-cache` exercises uv's download path without
clearing the existing cache or editing a project.

```bash
(
    set -eu
    wsl_probe_url='https://pypi.org/simple/requests/'
    curl --fail --show-error --location --max-time 20 \
        "$wsl_probe_url" -o /dev/null

    timeout --kill-after=5s 120s uv run --no-project --no-cache \
        --python /usr/bin/python3 --with requests python - "$wsl_probe_url" <<'PY'
import sys

import requests

with requests.get(sys.argv[1], timeout=(5, 15), stream=True) as response:
    response.raise_for_status()
    print("uv package download and Requests HTTPS check passed")
PY
)
```

A successful curl request alone does not establish that uv or Requests uses the
same certificate trust. A timeout is a failed check, not evidence of a TLS defect;
check connectivity and the approved proxy/index configuration before retrying.
When working in a project, follow that project's dependency instructions and
tests, using its normal locked command if it provides a lockfile.

## Target-machine smoke checks before declaring setup complete

Use an approved corporate Windows/WSL workstation for these checks; the
documentation itself cannot verify enterprise VPN, proxy, or administrator
policies. Do not include credentials or internal hostnames in shared logs.

| Scenario | Pass condition |
| --- | --- |
| Existing NAT + VPN | `wslinfo --networking-mode` matches the intended mode; internal DNS and an approved HTTPS endpoint work. |
| Normal WSL install | A new Ubuntu distro starts and its normal user is configured. |
| Store/default-path restriction | The relevant `--web-download` or `--location` fallback works; if blocked, the official rootfs `--import` recovery is documented and tested where permitted. |
| Explicit proxy or PAC-only environment | Proxy presence is checked without printing values; routing to an approved endpoint works or an IT-controlled mirror is identified. |
| APT behind proxy | `sudo apt update` succeeds with approved repository/proxy settings, without insecure bypasses. |
| uv with corporate CA | The uv installer HTTPS request and a separate uv dependency download succeed with the required certificate policy. |
| Disk-space maintenance | Follow the separate [compaction guide](wsl_4_disk_space.md) only if reclaiming storage is necessary; protect data first. |
