#!/bin/bash

# This script installs Docker Compose v2 on Ubuntu 20.04

set -e

# Ensure Docker is installed
if ! [ -x "$(command -v docker)" ]; then
  echo "Docker is not installed. Please install Docker before running this script."
  exit 1
fi

# Define the Docker Compose version to install
DOCKER_COMPOSE_VERSION="v2.20.2"

# Download Docker Compose binary
echo "Downloading Docker Compose $DOCKER_COMPOSE_VERSION..."
mkdir -p /usr/libexec/docker/cli-plugins
curl -SL "https://github.com/docker/compose/releases/download/$DOCKER_COMPOSE_VERSION/docker-compose-linux-$(uname -m)" -o /usr/libexec/docker/cli-plugins/docker-compose

# Apply executable permissions to the binary
echo "Applying executable permissions to Docker Compose binary..."
chmod +x /usr/libexec/docker/cli-plugins/docker-compose

# Create symbolic link to make docker-compose command available
echo "Creating symbolic link to /usr/local/bin/docker-compose..."
ln -s /usr/libexec/docker/cli-plugins/docker-compose /usr/local/bin/docker-compose

# Verify the installation
echo "Verifying Docker Compose installation..."
docker compose version
docker-compose version

echo "Docker Compose installation completed successfully!"
