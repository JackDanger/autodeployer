FROM alpine

COPY requirements.txt /tmp/requirements.txt
RUN apk add --no-cache --update openssh git python3 bash
RUN pip3 install --upgrade pip setuptools
RUN pip3 install -r /tmp/requirements.txt

ENV APP_DIR /app
ENV FLASK_APP app.py
ENV GIT_AUTHOR_NAME "Opsolutely Autodeployer"
ENV GIT_COMMITTER_NAME "Opsolutely Autodeployer"
ENV GIT_AUTHOR_EMAIL "autodeployer@opsolutely.com"
ENV GIT_COMMITTER_EMAIL "autodeployer@opsolutely.com"


RUN mkdir /root/.ssh
COPY ./.known_hosts /root/.ssh/known_hosts

# The CWD needs to be mounted at /app at run time
WORKDIR ${APP_DIR}
VOLUME ${APP_DIR}
EXPOSE 5000

# Cleanup
RUN rm -rf /.wh /root/.cache /var/cache /tmp/requirements.txt

CMD /usr/bin/flask run -h  0.0.0.0 -p 5000
