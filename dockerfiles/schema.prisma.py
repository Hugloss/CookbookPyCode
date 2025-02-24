generator client {
  provider = "prisma-client-py"
  binaryTargets = ["native", "rhel-openssl-1.1.x"]
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}