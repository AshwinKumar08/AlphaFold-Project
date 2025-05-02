FROM python:3.11
RUN apt-get update && apt-get upgrade -y
COPY requirements.txt /root/requirements.txt
RUN pip install -r /root/requirements.txt
RUN mkdir /app && mkdir /app/app && mkdir /app/data
RUN chown -R www-data:www-data /app
COPY startApp.sh /app/startApp.sh
WORKDIR /app
CMD ["/bin/bash", "/app/startApp.sh"]
