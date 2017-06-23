"""
Opsolutely Autodeployer

This app is a simple webservice that, when you GET /_status, will make
new git commits to itself and then push them to GitHub.
The commit only happens if the app has been booted for at least a
minute. If this app is automatically deployed on every git commit to
master then it functions as a self-deploying application.

Once the app has been up for ten minutes the /_status endpoint begins to
return HTTP 500 responses

Deploys, like unit tests, should never take ten minutes.

"""
import subprocess
import json
import os
from time import time
from flask_twisted import Twisted
from flask import Flask

process = subprocess.Popen(["git", "rev-parse", "HEAD"], stdout=subprocess.PIPE)
sha = process.communicate()[0].replace(b'\n', b'').decode('utf-8')
whoami = os.popen('whoami').read().replace('\n', '')
boot_time = time()
private_key_location = "/{}/.ssh/id_rsa".format(whoami)

app = Flask(__name__)
app.new_commit_added = False
twisted = Twisted(app)

"""
First we make sure we have the right RSA private key to push new commits
to GitHub
"""
try:
    os.open(private_key_location, os.O_RDONLY)
except FileNotFoundError:
    # We're in an environment with no private key set. We expect there
    # is one in the environment
    # TODO: read this secret from virtual filesystem so it's never
    # outside the process
    try:
        private_key = os.environ['PRIVATE_KEY']
    except KeyError:
        print("""
        To run this app you need to specify a PRIVATE_KEY env variable
        containing the contents of a private RSA key that can push to GitHub

        docker run -e PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY----- ..."
        """)
        exit(1)
    # Install the env-specified private key to ~/.ssh/id_rsa
    p = subprocess.Popen([
            'install',
            '-m',
            '600',
            '/dev/stdin',
            private_key_location,
        ], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
    p.communicate(input=private_key.encode('utf-8'))


@app.route('/_age')
def age():
    "Return a 200 or 500 HTTP response code based on time since boot"
    maybe_add_commit()
    age = time() - boot_time
    if age < 60 * 10:
        return "Recently deployed: {} seconds ago".format(int(age)), 200
    else:
        return "Deploy time is over 10-minute threshold: {} seconds ago".format(int(age)), 500


@app.route('/_status')
def status():
    "Display all about this instance"
    maybe_add_commit()
    return json.dumps({
            'sha': sha,
            'deploy_time': boot_time,
        })


@app.route('/')
def root():
    return """
        <h2>Current Autodeployer version: {}</h2>
        <pre><code>{}</code></pre>
    """.format(sha, status())


def maybe_add_commit():
    """
    If the app has been booted for at least a minute then make a new git
    commit, then no longer attempt this function for the life of the
    process.
    """
    if app.new_commit_added:
        return
    if boot_time + 60 < time():
        add_commit()
        app.new_commit_added = True


def add_commit():
    message = "{}".format(time())
    if 'COMMIT_HASH' in os.environ:
        message = message + " from {}".format(os.environ['COMMIT_HASH'])
    if 'ENVIRONMENT' in os.environ:
        message = message + " in {}".format(os.environ['ENVIRONMENT'])

    run(["git", "fetch", "origin", "master"])
    run(["git", "reset", "--hard", "origin/bump"])
    run(["git", "commit", "--allow-empty", "-m", message])
    run(["git", "push", "--force", "origin", "HEAD:bump"])


def run(cmd):
    subprocess.Popen(cmd, stdout=subprocess.PIPE)
    print(p.communicate()[0])

if __name__ == "__main__":
    app.run(host='0.0.0.0')
