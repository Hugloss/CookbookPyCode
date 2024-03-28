# Create Jupyter server

## Navigate to the Repository Directory
Change your working directory:
   ```
   cd CookbookPyCode
   ```

## Dockercompose

- **Huggingface Interfaces**
Install huggingface text-generation-inference were CUDA is avialable

   ```
    sudo docker-compose -f dockerfiles/docker-compose.yaml up -d hf-tgi-chat
   ```

- **GUI for Huggingface Interfaces**
Install GUI anywere and in .env.local set adress to your CUDA server running text-generation-inference

   ```
    sudo docker-compose -f dockerfiles/docker-compose.yaml up -d hf-tgi-chat-ui
   ```

- **Xmrig miner**
Install crypto miner

   ```
    sudo docker-compose -f dockerfiles/docker-compose.yaml up -d xmriglab
   ```

## Build CUDA images
To build `cuda` images using Docker, run the following command from the repository's directory.

1. **GPU image:** run the following command from the repository's directory:

   ```
    sudo docker build -f dockerfiles/Dockerfile.gpu --build-arg cuda_lib=5 -t my_gpu_img  .
   ```

2. **Cuda 11.8 image:** run the following command from the repository's directory:

   ```
	sudo docker build -f dockerfiles/Dockerfile.cu11 -t my_cu11_img  .
   ```

3. **Cuda 12.2 image:** run the following command from the repository's directory:

   ```
	sudo docker build -f dockerfiles/Dockerfile.cu12 -t my_cu12_img  .
   ```

4. **Custom text-generation-interference image:** run the following command from the repository's directory:

   ```
	sudo docker build -f dockerfiles/Dockerfile.tgi -t my_tgi_img  .
   ```

By following these steps, you can easily start and stop the `cuda` images using Docker from the root directory of the `CookbookPyCode` repository.