pip install -r requirements.txt

# export FLASK_APP=managedplatflasktest.py
# python -m flask run --host=0.0.0.0 --port=000

# examples for this came from: https://REDACTED.redhat.com/REDACTED/flask-basic-proxy/blob/master/run.sh
# and this site was helpful: https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https
gunicorn -b 0.0.0.0:000 managedplatflasktest:app --certfile /opt/app-root/cert/tls.crt --keyfile /opt/app-root/cert/tls.key