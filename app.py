import subprocess
import json
import time
from flask import Flask

process = subprocess.Popen(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE)
sha = process.communicate()[0].replace(b'\n', b'').decode('utf-8')
app = Flask(__name__)
boot_time = time.time()


@app.route('/_status')
def version():
    return json.dumps({
            'sha': sha,
            'deploy_time': boot_time,
        })


@app.route('/')
def root():
    return '<h2>Current Autodeployer version: {}</h2>'.format(sha)
