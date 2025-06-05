
# Install pyenv on Ubuntu / WSL

This guide will help you install `pyenv` and configure your shell environment. It also includes steps to install Python packages like `ipykernel` and `ipywidgets`.

---

## 🚀 1. Try Quick Install via `curl`

First, try installing with the official script:

```bash
curl https://pyenv.run | bash
````

If that **doesn't work** (e.g., due to SSL certificate errors), follow the manual install steps below.

---

## 🔧 2. Manual Install via Git
Clone pyenv and plugins:

```bash
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
git clone https://github.com/pyenv/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
git clone https://github.com/pyenv/pyenv-update.git ~/.pyenv/plugins/pyenv-update
```

---

## ⚙️ 3. Update `.bashrc`

Append the following to your `~/.bashrc`:

```bash
# pyenv setup
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

Reload your shell:

```bash
source ~/.bashrc
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

## 🐍 5. Install Python Packages

Once Python is set up via `pyenv`, install common Jupyter-related tools:

```bash
pip install ipykernel ipywidgets matplotlib pandas numpy
```

---

## 🎉 Done!

You're ready to use Python with `pyenv`, and tools like VS Code will work properly with `ipykernel` and `ipywidgets`.