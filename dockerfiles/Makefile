# Define variables
DOCKERFILE := dockerfiles/Dockerfile.myTest
IMAGE_NAME ?= myapp

# Default target
all: build

# Build using Dockerfile.myTest by default
build:
	@echo "Building image $(IMAGE_NAME) from $(DOCKERFILE)"
	docker build -f $(DOCKERFILE) -t $(IMAGE_NAME) .


# Allow overriding with a different Dockerfile
build-dockerfile-%:
	@echo "Building image $(IMAGE_NAME) from $*"
	docker build -f dockerfiles/$* -t $(IMAGE_NAME) .

# Run the container
run: build
	@echo "Running image $(IMAGE_NAME)"
	docker run --rm -it $(IMAGE_NAME)

# Clean up containers and images
clean:
	@echo "Cleaning up..."
	docker stop $$(docker ps -aq --filter ancestor=$(IMAGE_NAME)) 2>/dev/null || true
	docker rm $$(docker ps -aq --filter ancestor=$(IMAGE_NAME)) 2>/dev/null || true
	docker rmi $(IMAGE_NAME) 2>/dev/null || true

# Usage examples:
# make build         # Builds using Dockerfile.myTest by default
# make build-dockerfile-MyDockerfile   # Builds using dockerfiles/MyDockerfile
# make run           # Runs the built image
# make clean         # Cleans up containers and images
