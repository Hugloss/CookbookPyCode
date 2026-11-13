# Installing AI libraries with pip or uv

This is an **optional GPU/ML recipe**, not required by the basic WSL setup.
Unsloth and its CUDA/PyTorch dependencies require a supported GPU, driver and
Python stack; the procedure is **not** a CPU-only PyTorch installation guide.

First complete the [WSL corporate proxy, CA, and uv setup](wsl_3_uv_setup.md).
Use approved package indexes and sources. In a restricted environment, your
organization may provide its own package mirror.

## Option A: uv with an isolated virtual environment

For an Ubuntu 24.04 host with a compatible GPU and Python 3.12:

```bash
mkdir -p ~/src/unsloth-example
cd ~/src/unsloth-example
uv venv --python 3.12
uv pip install unsloth
```

`uv pip` automatically detects the local `.venv` even without shell
activation. To use it with other CLI tools, run
`source .venv/bin/activate`. Check the Unsloth support matrix for the
actual CUDA/Torch combination before training.

## Option B: pip with an isolated virtual environment

Use a separate environment; do not install large GPU dependencies into the
system Python. On Ubuntu 24.04, `python3` normally supplies Python 3.12:

```bash
mkdir -p ~/src/unsloth-pip-example
cd ~/src/unsloth-pip-example
python3 -m venv .venv
source .venv/bin/activate
python -m pip install unsloth
```

Do not use `--trusted-host` to bypass a missing corporate CA. See
[pip proxy and TLS troubleshooting](pyenv.md#6-repair-pip-proxy-or-tls-errors-without-disabling-verification).

## Advanced GPU version combinations

The earlier command mixed a fixed CUDA/Torch stack, moving Git branches, and
an unresolved `{install_numpy}` template token. That example was not runnable
or reproducible. Rather than guessing a compatible NumPy version, follow the
**current** vendor installation matrix for your hardware and freeze the tested
package versions in your project's requirements/lockfile. Avoid suppressing
package-installation diagnostics with `-qqq`.

References: [Unsloth pip installation](https://docs.unsloth.ai/get-started/installing-%2B-updating/pip-install),
[advanced Unsloth examples](https://docs.unsloth.ai/basics/gpt-oss-how-to-run-and-fine-tune/tutorial-how-to-fine-tune-gpt-oss),
and [uv environments](https://docs.astral.sh/uv/pip/environments/).
