#!/bin/bash

# Check if the correct number of arguments was provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <local network subnet> <path to export>"
    exit 1
fi

# Assigning arguments to variables
SUBNET=$1
EXPORT_PATH=$2

# Installing nfs-kernel-server if it is not already installed
if ! dpkg -l | grep -qw nfs-kernel-server; then
    echo "nfs-kernel-server is not installed. Installing..."
    sudo apt update
    sudo apt install nfs-kernel-server -y
fi

# Creating the export directory if it does not exist
if [ ! -d "$EXPORT_PATH" ]; then
    echo "The directory $EXPORT_PATH does not exist. Creating..."
    sudo mkdir -p "$EXPORT_PATH"
fi

# Setting up NFS export
echo "Exporting $EXPORT_PATH to the subnet $SUBNET with read-write access..."
sudo exportfs "$SUBNET":"$EXPORT_PATH" -o rw

echo "NFS export setup completed."
