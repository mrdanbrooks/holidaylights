#!/bin/bash

cd $HOME
git clone git@github.com:scanlime/fadecandy.git
cd fadecandy/server
make submodules
make

