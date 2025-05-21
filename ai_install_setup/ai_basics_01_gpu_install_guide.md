# GPU Installation Guide

## Check GPU for CUDA Capability
```bash
lspci | grep -i nvidia
```
[Verify CUDA-Capable GPU](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#verify-you-have-a-cuda-capable-gpu)

## Install CUDA Toolkit

Follow the official instructions for your system:
[CUDA Downloads for SLES 15 (RPM Network Installer)](https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=SLES&target_version=15&target_type=rpm_network)

### Verify CUDA Installation

After installation, verify that CUDA is installed correctly:

```bash
nvcc --version
```

### Install CUDA in Docker Image

For a **minimal build**, use:

```bash
zypper in cuda-minimal-build-12-4
```

For the **full toolkit**, use:

```bash
zypper in cuda-toolkit-12-4
```

> **Note:** Specifying the CUDA version (e.g., `12-4`) helps avoid automatic upgrades. If you prefer automatic updates, you can omit the version suffix.

### Prevent NVIDIA Driver Installation in Docker

Avoid installing drivers inside the Docker image by locking the related packages:

```bash
zypper addlock nvidia-driver-G06-kmp-default nvidia-open-driver-G06-kmp-default
```

---


## Installing the NVIDIA Container Toolkit
On the host, install NVIDIA Container Toolkit from:
[Nvidia Github](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#with-zypper-opensuse-sle).
```bash
# add the NVIDIA Container Toolkit repository directly from GitHub
sudo zypper ar https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo
# Install the NVIDIA container toolkit
sudo zypper --gpg-auto-import-keys install -y nvidia-container-toolkit
```

### View Current Version of NVIDIA Container Toolkit on Host Machine

The latest version of the NVIDIA Container Toolkit can be found here:
[NVIDIA Container Toolkit Release Notes](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/release-notes.html)

To check the installed version on your host system and verify its source, run:

```bash
zypper info nvidia-container-toolkit
```

Make sure the output includes the following:

```
Vendor         : NVIDIA CORPORATION
Upstream URL   : https://github.com/NVIDIA/nvidia-container-toolkit
```

> ⚠️ **Disclaimer:**
> Docker Compose may not work correctly unless the **NVIDIA Container Toolkit** is updated to the latest version. It’s recommended to always use the most recent release to ensure full compatibility with containerized GPU workloads.

## Configure the Docker Daemon
```bash
sudo nvidia-ctk runtime configure --runtime=docker
```

## Flush Changes and Restart Docker
```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

## Check Host Drivers
```bash
sudo nvidia-smi
```

## Check Docker's NVIDIA Runtime
```bash
cat /etc/docker/daemon.json
```
Look for:
```json
"runtimes": {
  "nvidia": {
    "path": "nvidia-container-runtime",
    "runtimeArgs": []
  }
},
"default-runtime": "nvidia"
```

## Check Docker Drivers
```bash
sudo docker run --rm --gpus all ubuntu nvidia-smi
```

If it returns an error:
```bash
docker: Error response from daemon: could not select device driver "" with capabilities: [[gpu]].
```
**Flush changes and restart Docker** has not been returned after the installation of **NVIDIA Container Toolkit**.

If you encounter driver issues inside the Docker container, check the [View version NVIDIA Container Toolkit](#view-version-nvidia-container-toolkit) section to ensure you're using a compatible setup.

If that is not working, test to reinstall, uninstall and install, the nvidia-container-toolkit.

## Create CUDA Container
Set variables in Dockerfile instead of on the `docker-run` command line:
```dockerfile
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
```
[More on Dockerfiles](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/docker-specialized.html#dockerfiles)

## Official Jupyter Image
```bash
sudo docker run --rm --gpus all tensorflow/tensorflow:latest-gpu-jupyter nvidia-smi
```

## Check GPU Usage
```bash
sudo docker run --rm --gpus all tensorflow/tensorflow:latest-gpu-jupyter python -c 'import torch; print(torch.cuda.is_available())'
sudo docker run --rm --gpus all tensorflow/tensorflow:latest-gpu-jupyter python -c 'import torch; print(torch.rand(2,3).cuda())'
```
[Reference](https://stackoverflow.com/a/59295489/1564762)

## Install Third-party Libraries
- [CUDA 11.8.0 Libraries](https://docs.nvidia.com/cuda/archive/11.8.0/cuda-installation-guide-linux/index.html#install-libraries)
- [CUDA 12.2.0 Libraries](https://docs.nvidia.com/cuda/archive/12.2.0/cuda-installation-guide-linux/index.html#install-third-party-libraries)

## Installing CUDA through Pip
- [Pip Wheels](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#pip-wheels)

```bash
RUN pip install \
    nvidia-cuda-runtime-cu12==12.1.105 \
    nvidia-cuda-nvrtc-cu12==12.1.105 \
    nvidia-cuda-cupti-cu12==12.1.105 \
    nvidia-cudnn-cu12==9.1.0.70 \
    nvidia-cublas-cu12==12.1.3.1 \
    nvidia-cufft-cu12==11.0.2.54 \
    nvidia-curand-cu12==10.3.2.106 \
    nvidia-cusolver-cu12==11.4.5.107 \
    nvidia-cusparse-cu12==12.1.0.106 \
    nvidia-nccl-cu12==2.20.5 \
    nvidia-nvtx-cu12==12.1.105 \
    nvidia-nvjitlink-cu12==12.1.105
```

### 🛠 Set Environment Variables (If Needed)

Sometimes, **PyTorch fails to find CUDA libraries at runtime**, even if they are installed correctly. This can happen due to environment variables not being set properly, especially in Docker containers or custom environments.

Even if the shared libraries (e.g., `libcublas.so`, `libcudnn.so`) **exist on disk**, PyTorch may not locate them unless their directories are listed in `LD_LIBRARY_PATH`.

#### 🔍 Diagnosing the Issue

To confirm that the `.so` files are present, use a command like:

```bash
find / -name 'libcudnn*'
find /usr/local/lib/python3.11/site-packages/ -name 'libcudnn.so*'
```

Replace `libcudnn.so*` with any library name you're troubleshooting (e.g., `libcublas.so*`, `libcufft.so*`, etc.).

If the files are found but PyTorch still fails to load them, it’s a sign that they’re not in the runtime linker’s search path.

#### ✅ Solution: Set `LD_LIBRARY_PATH`

You can fix this by explicitly adding all relevant library directories to the `LD_LIBRARY_PATH`. In a Dockerfile, use the `ENV` directive like this:

```dockerfile
ENV LD_LIBRARY_PATH=/usr/local/lib/python3.11/site-packages/nvidia/nvjitlink/lib:\
/usr/local/lib/python3.11/site-packages/nvidia/cupti/lib:\
/usr/local/lib/python3.11/site-packages/nvidia/nvtx/lib:\
/usr/local/lib/python3.11/site-packages/nvidia/cuda_nvrtc/lib:\
/usr/local/lib/python3.11/site-packages/nvidia/cuda_nvcc/lib:\
/usr/local/lib/python3.11/site-packages/nvidia/cuda_runtime/lib:\
/usr/local/lib/python3.11/site-packages/nvidia/cufile/lib:\
/usr/local/lib/python3.11/site-packages/nvidia/cusparse/lib:\
/usr/local/lib/python3.11/site-packages/nvidia/curand/lib:\
/usr/local/lib/python3.11/site-packages/nvidia/cusolver/lib:\
/usr/local/lib/python3.11/site-packages/nvidia/cufft/lib:\
/usr/local/lib/python3.11/site-packages/nvidia/cublas/lib:\
/usr/local/lib/python3.11/site-packages/nvidia/nccl/lib:\
/usr/local/lib/python3.11/site-packages/nvidia/cudnn/lib:\
/usr/local/lib/python3.11/site-packages/cusparselt/lib/:$LD_LIBRARY_PATH
```

## Locate `nvidia-smi`

To find the `nvidia-smi` package manually:

```bash
zypper se -f nvidia-smi
```

Zypper will show the package and may prompt to install it.

# CUDA Minimal Container

This project provides a minimal CUDA-enabled Docker container setup using Docker Compose. Follow the steps below to build, run, and validate the container functionality.

## Prerequisites

- Docker and Docker Compose installed
- NVIDIA GPU with drivers properly installed
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) set up
- Docker configured to support NVIDIA runtime

## Docker Compose Configuration

The `docker-compose.yaml` file is configured with a specific container name:

```yaml
version: "3.9"

services:
  cuda-minimal:
    container_name: cuda-min
    runtime: nvidia
    build:
      context: ./dockerfiles
      dockerfile: ./Dockerfile.cuda-min
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=all
    ...
```

## Steps to Run

### 1. Build and Start the Container

Use Docker Compose to build and start the container in detached mode:

```bash
docker compose up -d cuda-minimal
```

### 2. Access the Running Container

Enter the container with:

```bash
docker exec -it cuda-min /bin/bash
```

### 3. Validate Environment Inside the Container

Run the following commands to ensure everything is working correctly:

```bash
# Check GPU visibility
nvidia-smi

# Check zypper package manager functionality
zypper in -y unzip
```

If both commands succeed, it confirms:

- GPU access is working inside the container via NVIDIA Container Toolkit
- `zypper` is functioning properly inside the container
- Docker and NVIDIA configurations are correct

# Additional Resources
- [GitHub Gist](https://gist.github.com/denguir/b21aa66ae7fb1089655dd9de8351a202)
- [NVIDIA CUDA Docker Hub](https://hub.docker.com/r/nvidia/cuda)
- [GPU Jupyter on GitHub](https://github.com/iot-salzburg/gpu-jupyter)
- [AWS EC2 NVIDIA Driver Installation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/install-nvidia-driver.html)
- [NVIDIA Docker GitHub](https://github.com/NVIDIA/nvidia-docker)
- [NVIDIA Container Toolkit Install Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/1.13.5/install-guide.html#setting-up-docker)
- 📘 [CUDA Installation Guide for Linux (SLES)](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#common-installation-instructions-for-sles)
- 📦 [Minimal CUDA Installation for Smaller Footprint](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#upgrading-from-cudatoolkit-package)
