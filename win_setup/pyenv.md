# For windows run this and than follow the guide below
- https://github.com/pyenv-win/pyenv-win?tab=readme-ov-file#quick-start

# 🐍 Install `pyenv` on Ubuntu / WSL

This guide walks you through installing `pyenv`, setting up your shell, and configuring Python environments with essential packages like `ipykernel` and `ipywidgets`.

---

## 🚀 1. Quick Install via `curl`

Try the official one-liner installation script:

```bash
curl https://pyenv.run | bash
```

> ⚠️ If this fails (e.g., due to SSL issues), follow the manual installation steps below.

---

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

## 🛠 6. Fix pip SSL Issues (Optional)

If `pip` fails to connect to external resources (e.g., due to SSL errors), configure trusted hosts:

### 🔍 Check Current pip Configuration

```bash
pip config list
pip config debug
```

### ⚙️ Add Trusted Hosts

Set trusted hosts globally:

```bash
pip config set global.trusted-host "pypi.org files.pythonhosted.org pypi.python.org"
```

Verify the settings:

```bash
pip config list
```

---

## 🎉 You're All Set!

Python and `pyenv` are now installed and ready to use with tools like Jupyter and VS Code.