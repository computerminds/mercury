#!/bin/bash

# Main/Global Boot Script

# Config Memory
/etc/mercury/config_mem.sh

# Phone home - helps us to know how many users there are without passing any 
# identifying or personal information to us.
ID=`hostname | md5sum`
curl "http://getpantheon.com/pantheon.php?id=$ID&product=mercury"
