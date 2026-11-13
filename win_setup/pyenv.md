# For windows run this and than follow the guide below
- https://github.com/pyenv-win/pyenv-win?tab=readme-ov-file#quick-start

# 🐍 Install `pyenv` on Ubuntu / WSL

This guide walks you through installing `pyenv`, setting up your shell, and configuring Python environments with essential packages like `ipykernel` and `ipywidgets`.

---

## 🚀 1. Preferred official pyenv installer

In Ubuntu WSL, complete the [proxy and CA preflight](wsl_3_uv_setup.md)
before downloading scripts. Obtain the installer from an approved source:
[official pyenv-installer](https://github.com/pyenv/pyenv-installer).
Rather than piping a network response into Bash, download to a temporary file,
review it, and execute only when permitted by organizational policy:

```bash
pyenv_installer=$(mktemp)
curl --fail --show-error --location --max-time 60 \
    https://pyenv.run -o "$pyenv_installer"
# Inspect the file and check the upstream source before proceeding.
bash "$pyenv_installer"
rm -- "$pyenv_installer"
```

If this is blocked, use the manual Git installation below via the approved
corporate mirror or route. Do not bypass TLS verification to make it work.

## 🔧 2. Manual Installation via Git

Clone the main `pyenv` repo and its useful plugins:

```bash
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
git clone https://github.com/pyenv/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
git clone https://github.com/pyenv/pyenv-update.git ~/.pyenv/plugins/pyenv-update
```

---

## ⚙️ 3. Shell Configuration

Update your shell config (`~/.bashrc`, or `~/.zshrc` if using Zsh):

```bash
# pyenv setup
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

Then apply the changes:

```bash
source ~/.bashrc   # or `source ~/.zshrc`
```

---

## ✅ 4. Install Python with pyenv

Install and set a global Python version:

```bash
pyenv install 3.12
pyenv global 3.12
python --version
```

---

## 📦 5. Install Common Python Packages

Install useful Jupyter and data science packages:

```bash
pip install --upgrade setuptools pip wheel requests
pip install ipykernel ipywidgets matplotlib pandas numpy
```

---

## 🛠 6. Repair pip proxy or TLS errors without disabling verification

For Ubuntu WSL, use the [corporate proxy, APT and CA guide](wsl_3_uv_setup.md).
Configure the approved package index and trusted corporate root certificates
instead of adding public package hosts to pip's `trusted-host` exceptions.
An exception can weaken HTTPS verification.

Inspect pip's active configuration **locally**; do not paste values containing
proxy credentials or private indexes into shared logs:

```bash
python -m pip config list
python -m pip config debug
```

If an older recipe left `global.trusted-host` in your **user** pip
configuration, and `pip config debug` confirms it exists at that scope,
remove only that key:

```bash
python -m pip config --user unset global.trusted-host
```

Other possible sources include a virtual-environment/site configuration,
system-managed config, or the `PIP_TRUSTED_HOST` environment variable. Remove
only exceptions you own; ask IT before changing managed settings. See
[pip configuration](https://pip.pypa.io/en/stable/cli/pip_config/) and
[pip HTTPS certificates](https://pip.pypa.io/en/stable/topics/https-certificates/).

## 🎉 You're All Set!

Python and `pyenv` are now installed and ready to use with tools like Jupyter and VS Code.