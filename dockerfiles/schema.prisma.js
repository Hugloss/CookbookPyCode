generator client {
  provider = "prisma-client-js"
  binaryTargets = ["native", "rhel-openssl-1.1.x"]
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}