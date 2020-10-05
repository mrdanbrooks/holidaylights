#!/bin/bash

cd $HOME
git clone git@github.com:scanlime/fadecandy.git
cd fadecandy/server
make submodules
make

# Add User to tty group
# sudo usermod -a -G tty pi
