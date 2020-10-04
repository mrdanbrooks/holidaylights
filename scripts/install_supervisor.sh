#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Install dependencies
sudo apt-get install supervisor



# Link config files to supervisor
sudo ln -s $DIR/supervisor/lights.conf /etc/supervisor/conf.d/lights.conf
sudo ln -s $DIR/supervisor/fadecandy.conf /etc/supervisor/conf.d/fadecandy.conf
