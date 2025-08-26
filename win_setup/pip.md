
# 🧩 AI Libraries Installation Guide

We use **[Unsloth](https://github.com/unslothai/unsloth)** as the base framework to install and manage AI libraries.
Unsloth provides optimized training utilities, integrations, and dependencies for **PyTorch**, **Transformers**, and other GPU-accelerated packages.
This guide shows you how to install the required AI libraries using either **pip** or **uv**.
Choose the method that best fits your workflow.
---

## 🚀 Install with pip

You can install **Unsloth** with CUDA 12.4 and Torch 2.5.0 support directly via pip:

```bash
pip install "unsloth[cu124-torch250] @ git+https://github.com/unslothai/unsloth.git"
```

📖 Reference: [Unsloth Docs – Advanced Pip Installation](https://docs.unsloth.ai/get-started/installing-+-updating/pip-install#advanced-pip-installation)

---

## ⚡ Install with uv

If you prefer using **uv**, you can install the dependencies with:

```bash
uv pip install -qqq \
    "torch>=2.8.0" "triton>=3.4.0" {install_numpy} \
    "unsloth_zoo[base] @ git+https://github.com/unslothai/unsloth-zoo" \
    "unsloth[base] @ git+https://github.com/unslothai/unsloth" \
    torchvision bitsandbytes \
    git+https://github.com/huggingface/transformers \
    git+https://github.com/triton-lang/triton.git@05b2c186c1b6c9a08375389d5efe9cb4c401c075#subdirectory=python/triton_kernels
```

📖 Reference: [Fine-tuning GPT-OSS with Unsloth](https://docs.unsloth.ai/basics/gpt-oss-how-to-run-and-fine-tune/tutorial-how-to-fine-tune-gpt-oss)
