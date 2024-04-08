FROM python:3.9

WORKDIR /var/www/vhosts/terraform-gui.com/public_html
ENV FLASK_APP=blog

COPY ./app2_new/requirements.txt ./
COPY ./app2_new/uwsgi.ini ./
COPY ./shell/setup.sh /root

RUN pip install --upgrade pip \
    && pip install --upgrade setuptools \
    && pip install -r requirements.txt \
    && apt-get update -y \
    && apt-get install -y vim less unzip ansible \
    && chmod +x /root/setup.sh \
    && /root/setup.sh