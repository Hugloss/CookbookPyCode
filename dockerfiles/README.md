# Create Jupyter server

## Navigate to the Repository Directory
Change your working directory:
   ```
   cd CookbookPyCode
   ```

## Build images
To build `cuda` images using Docker, run the following command from the repository's directory.

1. **GPU image:** run the following command from the repository's directory:

   ```
    sudo docker build -f dockerfiles/Dockerfile.gpu --build-arg cuda_lib=4 -t my_gpu_img  .
   ```

2. **Cuda 11.8 image:** run the following command from the repository's directory:

   ```
	sudo docker build -f dockerfiles/Dockerfile.cu11 -t my_cu11_img  .
   ```

3. **Cuda 12.2 image:** run the following command from the repository's directory:

   ```
	sudo docker build -f dockerfiles/Dockerfile.cu12 -t my_cu12_img  .
   ```


By following these steps, you can easily start and stop the `cuda` images using Docker from the root directory of the `CookbookPyCode` repository.