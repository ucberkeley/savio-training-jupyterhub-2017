#!/bin/bash
cat >> ipcontroller_config.py << EOF
import netifaces
c.IPControllerApp.location = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
c.HubFactory.ip = '*'
EOF
