#!/bin/bash

# cat /etc/pki/tls/cert.pem >> /opt/app-root/src/custom-cert.pem  # this pulls the default public key certificates  # TODO still necessary even with egress rules?
# echo -e "\n # copy of /opt/app-root/src/cert/REDACTED \n" >> /opt/app-root/src/custom-cert.pem  # this makes sure the files are spaced
# cat /opt/app-root/src/cert/REDACTED >> /opt/app-root/src/custom-cert.pem  # and this is the cert for communicating between pods, namely for >>> push_to_gateway() to access pushgateway

gunicorn -b 0.0.0.0:000 visor_flask:app --certfile /opt/app-root/cert/tls.crt --keyfile /opt/app-root/cert/tls.key --daemon
python visor_main.py

# python app.py $1