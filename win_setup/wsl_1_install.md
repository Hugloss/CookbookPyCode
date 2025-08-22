# 🐧 Install WSL & Ubuntu 24.04 (Manual Method)

Follow these steps to install WSL and manually import Ubuntu 24.04.

---

## ⚙️ 1. Update WSL Using Web Download

```bash
wsl --update --web-download
```

## 🔍 2. Check WSL Status

```bash
wsl --status
```

---

## 🛠️ 3. Try Installing Ubuntu Automatically

```bash
wsl --install Ubuntu
```

> ✅ If this works, you're done!
> ❌ If it fails (e.g., due to permission issues with the default install path), continue with the manual installation below.

---

## 📦 4. Download Ubuntu 24.04 Image

Download the official `.gz` WSL image from Ubuntu:

🔗 [Download Ubuntu 24.04 for WSL](https://ubuntu.com/desktop/wsl)

---

## 📁 5. Navigate to the Download Location

Use your terminal to move into the directory where the image was downloaded:

```bash
cd $HOME/Downloads
```

> If you're using PowerShell or CMD, adjust the path to your `Downloads` folder accordingly.

---

## 📥 6. Import Ubuntu into WSL Manually

Replace the paths and filename as needed:

```bash
wsl --import Ubuntu-24.04 "C:\Ubuntu" .\ubuntu-24.04.2-wsl-amd64.gz
```

---

## 🚀 7. Launch Ubuntu

Start the newly imported distro:

```bash
wsl -d Ubuntu-24.04
```

---

# 🛠️ Ubuntu Development Environment Setup

Set up a robust development environment for software development on Ubuntu.

---

## 🔄 Step 1: Update Package Index

Start WSL and run:

```bash
sudo apt update
```

---

## 📦 Step 2: (Optional) Upgrade System Packages

List available upgrades:

```bash
apt list --upgradable
```

To upgrade all packages:

```bash
sudo apt full-upgrade -y
```

---

## 🧰 Step 3: Install Development Tools & Libraries

Install essential build tools and libraries:

```bash
sudo apt install -y \
  make build-essential libssl-dev zlib1g-dev libbz2-dev \
  libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
  xz-utils tk-dev libxml2-dev libffi-dev liblzma-dev \
  python-is-python3 libxmlsec1-dev libcurl4-openssl-dev \
  rsync zip g++ gdb ninja-build
```

These tools cover C, C++, Python development, and general compilation needs.

---

## 📚 References

* [Microsoft WSL Install Guide](https://learn.microsoft.com/en-us/windows/wsl/install)
* [Ubuntu WSL Documentation](https://documentation.ubuntu.com/wsl/latest/howto/install-ubuntu-wsl2/)
* [Build & Debug in WSL2 with MSVC](https://learn.microsoft.com/en-us/cpp/build/walkthrough-build-debug-wsl2?view=msvc-170#install-the-build-tools)
* [WSL Setup Gist](https://gist.github.com/ScriptAutomate/f94cd44dacd0f420fae65414e717212d?permalink_comment_id=3627426)
