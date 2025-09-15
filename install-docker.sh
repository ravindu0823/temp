#!/bin/bash

# This script installs Docker on Ubuntu 20.04

set -e

# Update existing list of packages
echo "Updating package list..."
apt update

# Install prerequisite packages
echo "Installing prerequisite packages..."
apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
echo "Adding Docker's GPG key..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -

# Add the Docker repository to APT sources
echo "Adding Docker repository..."
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"

# Update package database with Docker packages from the newly added repo
echo "Updating package list again..."
apt update

# Install Docker
echo "Installing Docker..."
apt install -y docker-ce

# Add the current user to the 'docker' group
if [ "$SUDO_USER" ]; then
  echo "Adding user '$SUDO_USER' to the 'docker' group..."
  usermod -aG docker $SUDO_USER
  echo "User '$SUDO_USER' added to 'docker' group. Please log out and back in for changes to take effect."
fi

# Enable Docker service to start on boot
echo "Enabling Docker to start on boot..."
systemctl enable docker

# Start Docker service
echo "Starting Docker service..."
systemctl start docker

# Verify Docker installation
echo "Verifying Docker installation..."
docker --version

# Test Docker installation
echo "Running a test Docker container..."
docker run hello-world

echo "Docker installation completed successfully!"
