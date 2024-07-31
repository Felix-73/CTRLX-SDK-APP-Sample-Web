from flask import Flask, redirect, render_template, request, session, url_for, Response, Blueprint

import os
from werkzeug.serving import run_simple
from werkzeug.middleware.proxy_fix import ProxyFix


##settings 

dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
app = Flask(__name__, static_url_path='')

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

os.chdir(dir_path)



########## serving functions

@app.route('/sample-flask/')
def index():
    
    return app.send_static_file('sample-flask/index.html')

##server start

if __name__ == '__main__':
  

    if "SNAP_DATA" in os.environ:
        run_simple('unix://'+os.environ['SNAP_DATA']+'/package-run/sample-flask-webapp/example.sock', 0, app)
        #app.run(host='0.0.0.0',debug = False, port=3125)
    else:

        app.run(host='0.0.0.0',debug = False, port=12121)

