#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Install dependencies
# https://stackoverflow.com/a/22592801
if [ $(dpkg-query -W -f='${Status}' supervisor 2>/dev/null | grep -c "ok installed") -eq 0 ];
then
    sudo apt-get install supervisor
fi



# Link config files to supervisor
sudo ln -s $DIR/../supervisor/shutdown_service.conf /etc/supervisor/conf.d/shutdown_service.conf

# restart supervisor
sudo systemctl restart supervisor.service
