#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Install dependencies
sudo apt-get install supervisor



# Link config files to supervisor
sudo ln -s $DIR/../supervisor/neopixel_lights.conf /etc/supervisor/conf.d/neopixel_lights.conf
sudo ln -s $DIR/../supervisor/inet.conf /etc/supervisor/conf.d/inet.conf
