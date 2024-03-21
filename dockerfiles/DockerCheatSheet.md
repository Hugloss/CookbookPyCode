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
sudo docker exec -it [CONTAINER_ID] /bin/bash
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
   sudo docker stop [CONTAINER_ID_OR_NAME]
   ```

3. **Remove the Container.**

   Now, you can remove the container using:

   ```bash
   sudo docker rm [CONTAINER_ID_OR_NAME]
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

- [Docker Cheatsheet][def]

[def]: https://dockerlabs.collabnix.com/docker/cheatsheet/