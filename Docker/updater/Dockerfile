FROM python:latest
RUN apt-get update && apt-get install -y cron

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

COPY crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab
RUN /usr/bin/crontab /etc/cron.d/crontab
RUN echo $PYTHONPATH
CMD ["cron", "-f"]