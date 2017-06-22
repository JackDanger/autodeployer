import subprocess
import json
from time import time
from flask import Flask

process = subprocess.Popen(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE)
sha = process.communicate()[0].replace(b'\n', b'').decode('utf-8')
app = Flask(__name__)
app.new_commit_added = False
boot_time = time()


@app.route('/_status')
def version():
    maybe_add_commit()
    return json.dumps({
            'sha': sha,
            'deploy_time': boot_time,
        })


@app.route('/')
def root():
    return '<h2>Current Autodeployer version: {}</h2>'.format(sha)


def maybe_add_commit():
    """
    If the app has been booted for at least a minute then make a new git
    commit, then no longer attempt this function for the life of the
    process.
    """
    if app.new_commit_added:
        return
    if boot_time + 2 < time():
        add_commit()
        app.new_commit_added = True


def add_commit():
    subprocess.Popen(["git", "commit", "--allow-empty", "-m", "time()"], stdout=subprocess.PIPE)
    subprocess.Popen(["git", "push", "origin", "master"], stdout=subprocess.PIPE)
