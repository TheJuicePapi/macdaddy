#!/bin/bash

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit
fi

# Install python3, macchanger, iproute2
echo "Installing pip and Pillow..."
sudo apt-get update
sudo apt-get install -y python3
sudo apt-get install -y macchanger
sudo apt-get install -y iproute2

# Create symbolic link for macdaddy.py
ln -s "$(pwd)/macdaddy.py" /usr/local/bin/macdaddy

clear

echo "Installation complete. You can now run 'macdaddy' from any directory."
