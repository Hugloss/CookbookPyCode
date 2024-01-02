# GPU Installation Guide

## Check GPU for CUDA Capability
```bash
lspci | grep -i nvidia
```
[Verify CUDA-Capable GPU](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#verify-you-have-a-cuda-capable-gpu)

## Installing the NVIDIA Container Toolkit
On the host, install NVIDIA Container Toolkit from [here](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).
```bash
sudo zypper --gpg-auto-import-keys install -y nvidia-container-toolkit
```

## Install CUDA Toolkit
Follow the instructions for your system [here](https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=SLES&target_version=15&target_type=rpm_network).

Check CUDA install:
```bash
nvcc --version
```

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

## Additional Resources
- [GitHub Gist](https://gist.github.com/denguir/b21aa66ae7fb1089655dd9de8351a202)
- [NVIDIA CUDA Docker Hub](https://hub.docker.com/r/nvidia/cuda)
- [GPU Jupyter on GitHub](https://github.com/iot-salzburg/gpu-jupyter)
- [AWS EC2 NVIDIA Driver Installation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/install-nvidia-driver.html)
- [NVIDIA Docker GitHub](https://github.com/NVIDIA/nvidia-docker)
- [NVIDIA Container Toolkit Install Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/1.13.5/install-guide.html#setting-up-docker)