# everything here is almost verbatim examples from the web for "hello world flask" apps

from flask import Flask
app = Flask(__name__)

@app.route('/health')  # necessary for the livenessProbes
def health():
    return "available", 000

@app.route('/')
def hello_world():
    return 'ViSOR Monitoring is running'

if __name__ == "__main__":
    # learned this syntax from https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https
    app.run(ssl_context=('/opt/app-root/cert/tls.crt',  
                         '/opt/app-root/cert/tls.key'
                         ))
