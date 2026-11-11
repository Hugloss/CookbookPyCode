# Python and uv inside WSL

Use this guide after [installing WSL](wsl_1_install.md) and checking the
[network configuration](wsl_2_dns_fix.md). All commands below run **inside Ubuntu
in WSL**, as your normal Linux user; only commands marked `sudo` need Linux root.
For the full sequence, see the [Windows setup index](README.md).

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

If HTTPS fails behind a corporate proxy, complete the approved-CA procedure below
before downloading tools. Mirrored networking and proxy forwarding do not install
the organization's CA certificate into Ubuntu.

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

# uv >= 0.11.0: use the CA trust installed inside this WSL distro.
export UV_SYSTEM_CERTS=true
```

The explicit cache path is usually already uv's Linux default. System certificate
selection is useful when Ubuntu trusts an approved corporate CA; it is not needed
for every public-network setup. Leave `UV_LINK_MODE` unset for normal operation.

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

## Optional: corporate CA trust and explicit bundles

Obtain the organization's approved **CA certificate**, verify it through your IT
team, and save it as a PEM-format `.crt` file. Install it in Ubuntu, replacing the
example source path:

```bash
sudo install -m 0644 /path/to/approved-company-ca.crt \
    /usr/local/share/ca-certificates/company-ca.crt
sudo update-ca-certificates
```

Follow [Ubuntu's CA installation guide](https://ubuntu.com/server/docs/how-to/security/install-a-root-ca-certificate-in-the-trust-store/).
Installing the CA on Windows alone is not this Ubuntu installation step.
Never use disabled TLS verification to work around a missing trusted CA.

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
unwanted global `UV_LINK_MODE=copy`. Editing a file does not remove variables
already inherited by a running process. After editing, unset only the settings
you intentionally retired, for example:

```bash
unset UV_NATIVE_TLS UV_LINK_MODE
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
