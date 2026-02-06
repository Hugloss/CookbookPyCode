# Define variables
DOCKERFILE := Dockerfile
IMAGE_NAME ?= myapp

# Default target
all: build

# Build using Dockerfile.myTest by default
build:
	@echo "Building image $(IMAGE_NAME) from $(DOCKERFILE)"
	docker build -f $(DOCKERFILE) -t $(IMAGE_NAME) .

# Run the container
run: build
	@echo "Running image $(IMAGE_NAME)"
	docker run --rm -it $(IMAGE_NAME)

# Run an interactive bash shell
run-bash: build
	@echo "Running bash in $(IMAGE_NAME)"
	docker run --rm -it --entrypoint /bin/bash $(IMAGE_NAME)


# Run with GPU(s) using the image's default CMD
run-gpu: build
	@echo "Running bash in $(IMAGE_NAME) with GPUs"
	docker run --env-file .env --rm -it --gpus all --entrypoint /bin/bash $(IMAGE_NAME)