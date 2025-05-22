# Docker Cheatsheet

---

## Overview of Docker Images

### View Available Images

To see the list of Docker images on your system, use the following command:

```bash
sudo docker images
```

The output provides a detailed overview, including repository names, tags, image IDs, creation times, and sizes.

- **REPOSITORY**: The name of the repository.
- **TAG**: The version or tag of the image.
- **IMAGE ID**: Unique identifier.
- **CREATED**: Time since creation.
- **SIZE**: Image size.

The output of the `sudo docker images` command will look something like this:

```bash
REPOSITORY             TAG       IMAGE ID       CREATED         SIZE
ubuntu                 20.04     775349758637   2 weeks ago     73.3MB
nginx                  latest    abd3a4a9e58d   3 weeks ago     133MB
alpine                 3.14      e7d92cdc71fe   4 weeks ago     5.61MB
```

## Dangling Images

To view dangling images, use the following command:

```bash
sudo docker images -f "dangling=true"
```

## Container Overview

To list all containers, both running and stopped, use:

```bash
sudo docker ps -a
```

The output includes container ID, image, command, creation time, status, ports, and names.

- **CONTAINER ID**: Unique identifier.
- **IMAGE**: Docker image used.
- **COMMAND**: Command used to start the container.
- **CREATED**: Time since creation.
- **STATUS**: Current status (e.g., Up, Exited).
- **PORTS**: Mapped ports.
- **NAMES**: Assigned names.

The output of the `sudo docker ps -a` command will look something like this:

```
CONTAINER ID   IMAGE             COMMAND                  CREATED         STATUS                      PORTS       NAMES
2b3e0177a422   ubuntu:latest     "/bin/bash"              2 days ago      Exited (0) 2 days ago                   nostalgic_jennings
c3f279d17e0a   ubuntu:latest     "/bin/bash"              3 days ago      Exited (1) 3 days ago                   determined_sammet
a1b2c3d4e5f6   nginx:latest      "nginx -g 'daemon of…"   5 days ago      Up 5 days                   80/tcp      web_server
```

## Build Local Image

To build a local image, use:

```bash
sudo docker build -t CUSTOM_IMAGE_NAME .
```

when build another dockerfile with CUSTOM_DOCKERFILE_NAME

```bash
sudo docker build -f CUSTOM_DOCKERFILE_NAME -t CUSTOM_IMAGE_NAME  .
```

## Interacting with Containers

### Starting a Shell in a Running Container

To enter a running container, use:

```bash
sudo docker exec -it [CONTAINER_NAME_OR_ID] /bin/bash
```

### Launching an Image Interactively

To start a Docker image interactively, use:

```bash
sudo docker run -it --rm [IMAGE_NAME_OR_ID] /bin/bash

sudo docker run -it --entrypoint '' --rm [IMAGE_NAME_OR_ID] /bin/bash
```

### Stop interacting with containers

To gracefully stop a container interactively, use the keyboard shortcut:

```
Ctrl + D
```

## Restarting a Docker Container

Sometimes a container may hang, misbehave, or need to be refreshed after changes. Restarting it ensures a clean state without affecting the underlying image or volumes.

### Stop the Running Container

Stops the container gracefully.

```bash
docker compose stop [IMAGE_NAME_OR_ID]
> ✔ Container [CONTAINER_NAME_OR_ID] Stopped  # Expected output:
```

### Remove the Existing Container

Removes the stopped container. This is safe and doesn't delete your image or persistent data (if volumes are used).

```bash
docker rm [CONTAINER_NAME_OR_ID]
> [CONTAINER_NAME_OR_ID]  # Expected output:
```

### Start a Fresh Instance

Brings the container back up using the configuration in `docker-compose.yml`.

```bash
docker compose up -d [IMAGE_NAME_OR_ID]
> Creating [CONTAINER_NAME_OR_ID] ... done  # Expected output:
```

## Remove existing container

1. **Identify the Container ID or Name.**

   First, list all containers to find the ID or name of the one you want to remove:

   ```bash
   sudo docker ps -a
   ```

   This will display all containers, both running and stopped. Note down the CONTAINER ID or NAMES of the container you wish to remove.

2. **Stop the Container (if it's running).**

   Before you can remove a container, you must ensure it's stopped. To stop a container, use:

   ```bash
   sudo docker stop [CONTAINER_NAME_OR_ID]
   ```

3. **Remove the Container.**

   Now, you can remove the container using:

   ```bash
   sudo docker rm [CONTAINER_NAME_OR_ID]
   ```

## Docker File Cleanup

These commands free up disk space by removing untagged and unreferenced images.

### Removing Images by ID

```bash
sudo docker rmi [IMAGE_ID]
```

### Removing unreferenced Images

Clean up dangling and unused images using the following commands:

### Cleanup dangling images.

```bash
sudo docker image prune -f
```

**WARNING!** This command will remove:

- All dangling images.


### Cleanup unused images and dangling ones.

```bash
sudo docker image prune --all -f
```

**WARNING!** This command will remove:

- All images without at least one container associated with them


### List dangling images

To get the list of dangling images, you can use the following command:

```bash
sudo docker images -f "dangling=true"
```

## Docker System Cleanup

This provides clear instructions on how to perform Docker system cleanup and obtain a list of exited containers. These commands free up disk space by removing unused containers and images.


### Docker System Prune

To clean up all unused containers in one command, you can use the following Docker command:

```bash
docker system prune --all -f
```

**WARNING!** This command will remove:

- All stopped containers
- All volumes not used by at least one container
- All images without at least one container associated with them

### List Exited Containers

To get the list of exited containers, you can use the following command:

```bash
sudo docker ps -a -f status=exited
```


---

# 🚀 Docker Compose Quick Guide

Docker Compose is a powerful tool that simplifies managing multi-container Docker applications. Instead of manually running multiple `docker` commands for each container, network, or volume every time you start or stop a service, **Docker Compose lets you define everything in a single YAML file** and manage it with just a few simple commands.

Using Docker Compose is especially helpful because:

* ✅ **Consistency**: All services, volumes, networks, and environment variables are defined in one place (`docker-compose.yml`), reducing human error.
* 🔄 **Reproducibility**: Teams and CI pipelines can spin up identical environments using the same configuration file.
* 🚀 **Efficiency**: Start up all services (`web`, `db`, `cache`, etc.) at once with a single `up` command—no need to remember or type individual `docker run` commands.
* 🧪 **Easy Testing & Debugging**: You can quickly rebuild, restart, or exec into containers for testing and verification, which speeds up development and debugging.
* 🛠️ **Cleaner Workflow**: Compose keeps your Docker commands cleaner and shorter, especially when working with complex apps that have many moving parts.

This guide covers the essential `docker compose` commands for building, running, stopping, and troubleshooting containers, as well as tips for interacting with running services more effectively.

---

## 📦 Build Containers

Standard build command:

```bash
docker compose -f [IMAGE_NAME_OR_ID] build
```

---

### 🛠️ Build Hanging or Not Starting?

Sometimes, when you run `docker compose build`, the process may appear to hang, not output anything, or take an unusually long time to start. This is often related to **BuildKit**, Docker's newer build backend, which can be problematic in some environments or CI systems.

To resolve this:

* Disable BuildKit by setting `DOCKER_BUILDKIT=0`
* Enable plain text progress output with `--progress=plain` for better visibility into each build step

Use this command:

```bash
DOCKER_BUILDKIT=0 docker compose -f [IMAGE_NAME_OR_ID] build --progress=plain
```

This often helps you identify exactly where the build is getting stuck and can help avoid silent failures or hanging issues.

---

## 🔼 Run Containers in Background

To run containers in detached mode:

```bash
docker compose -f [IMAGE_NAME_OR_ID] up -d
```

---

## ⏹️ Stop Containers

To stop and remove all running containers:

```bash
docker compose -f [IMAGE_NAME_OR_ID] down
```

---

## 🔍 Interact with a Running Container

To simplify debugging or verifying tasks inside a container:

### Step 1: Assign a Name in the Compose File

In your `docker-compose.yml` or equivalent file:

```yaml
services:
  my_service:
    container_name: my_named_container
    ...
```

This makes it easier to reference the container later.

### Step 2: Exec into the Running Container

Once the container is up, use the name you assigned:

```bash
docker exec -it my_named_container /bin/bash
```

This lets you easily enter the container to inspect logs, run commands, or test dependencies directly.

---

## ✅ Summary of Key Commands

| Task                        | Command                                                                         |
| --------------------------- | ------------------------------------------------------------------------------- |
| Build                       | `docker compose -f [IMAGE_NAME_OR_ID] build`                                    |
| **Build (when stuck)**      | `DOCKER_BUILDKIT=0 docker compose -f [IMAGE_NAME_OR_ID] build --progress=plain` |
| Up (detached)               | `docker compose -f [IMAGE_NAME_OR_ID] up -d`                                    |
| Stop                        | `docker compose -f [IMAGE_NAME_OR_ID] down`                                     |
| Exec into a named container | `docker exec -it <container_name> /bin/bash`                                    |


Absolutely! Here's a beginner-friendly, fully explained **README-style Markdown** summary that covers:

* Why you should use a `Makefile` with Docker Compose
* Clear, real-world examples
* Explanations geared toward someone new to both Docker and Make

---

# ⚙️ Automating Docker with Makefile + Docker Compose

This guide explains why and how to use a `Makefile` to automate Docker Compose commands, even if you're new to both.

---

## 🤔 Why Use a `Makefile`?

When working with Docker Compose, you often repeat the same commands over and over:

```bash
docker compose -f docker-compose.yml build
docker compose -f docker-compose.yml down
docker compose -f docker-compose.yml up -d
```

Doing this manually is:

* 🥱 Repetitive
* 🧠 Easy to mess up
* 🐢 Slows you down

A **Makefile** solves this by letting you define **easy one-word commands** like:

```bash
make start
make build
make start_gpu
```

---

## 🛠️ What is a `Makefile`?

A `Makefile` is just a file named `Makefile` (no file extension) where you define shortcuts for terminal commands. Each shortcut is called a **target**.

Instead of remembering and typing complex Docker commands every time, you can type simple `make` commands.

---

## 🧱 Example `Makefile`

```makefile
# Default Docker Compose file
COMPOSE=docker compose -f docker-compose.yml

# Container name to exec into (should match `container_name:` in your docker-compose.yml)
CONTAINER=my_named_container

# Start sequence: Build first, then stop and start fresh containers
# This ensures your app is only taken down if the build succeeds
start: build down up

# Build Docker images with BuildKit disabled for better troubleshooting
# --progress=plain gives you full build output
build:
	DOCKER_BUILDKIT=0 $(COMPOSE) build --progress=plain

# Stop and remove containers, networks, and optionally volumes
# Ensures a clean start
down:
	$(COMPOSE) down

# Start containers in detached (background) mode
up:
	$(COMPOSE) up -d

# Start GPU-based services using a different Docker Compose file
# Overrides the COMPOSE variable to point to docker-compose.gpu.yml
start_gpu:
	$(MAKE) start COMPOSE="docker compose -f docker-compose.gpu.yml"

# Open a shell inside the running container
# Useful for debugging or manual testing
shell:
	docker exec -it $(CONTAINER) /bin/bash

# Stream logs from all containers in real time
logs:
	$(COMPOSE) logs -f

# Run a PyTorch GPU availability check inside the container
# This helps confirm that CUDA is working properly
test:
	docker exec -it $(CONTAINER) python -c "import torch; print(torch.cuda.is_available())"

```

---

## 🧪 How to Use It

In your terminal:

```bash
make start
```

This runs:

```bash
docker compose -f docker-compose.yml build
docker compose -f docker-compose.yml down
docker compose -f docker-compose.yml up -d
```

For GPU-specific containers:

```bash
make start_gpu
```

This switches the Compose file to `docker-compose.gpu.yml`.

---

## 💡 Why This Is Better

| Without Make                             | With Make                          |
| ---------------------------------------- | ---------------------------------- |
| Typing 3+ commands each time             | One command (`make start`)         |
| High chance of typos                     | Safe, repeatable tasks             |
| Hard to remember flags                   | Flags are hidden in the Makefile   |
| Team needs to learn every Docker command | Team runs the same `make` commands |


---

## ✅ Final Tip for Beginners

Think of your Makefile as your "remote control" for Docker. It runs all the hard-to-remember Docker commands so you can focus on building, testing, and coding.

---

## 🚨 Critical Risk with `down` Before Successful Build

If you use this pattern:

```bash
docker compose down
docker compose up -d --build
```

You're taking a risk:

1. **Step 1: `down`**
   You immediately stop and remove all running containers — your app is now offline.

2. **Step 2: `up -d --build`**
   If the build **fails**, nothing gets started.
   ➜ Your app stays **down** until the issue is fixed.

---

## ✅ Why `build → down → up -d` is Safer

```bash
docker compose build
docker compose down
docker compose up -d
```

With this pattern:

1. **Step 1: Build First**

   * If the build fails, your existing app is **still running**.
   * No downtime is introduced.
   * You have time to fix the issue before trying again.

2. **Step 2: Down + Up only if build succeeds**

   * Only take your app offline **after** a successful image is built.
   * This makes it safe and predictable in production, staging, or live demos.

---

## 🧠 Summary: Why `build` First is Better

| Scenario                         | `down → up --build`      | `build → down → up`     |
| -------------------------------- | ------------------------ | ----------------------- |
| If build **fails**               | App is offline           | App stays online        |
| Safer for production?            | ❌ No                     | ✅ Yes                   |
| Easier to debug failed build     | ❌ Mixed with `up` errors | ✅ Clean build-only step |
| Time to fix build before restart | ❌ App already down       | ✅ App still running     |

---

💡 **Rule of thumb**: Always **build first, take down later**, unless you’re absolutely sure the build will succeed and you’re in a non-critical environment (e.g., local dev).

---

- [Docker Cheatsheet][def]

[def]: https://dockerlabs.collabnix.com/docker/cheatsheet/