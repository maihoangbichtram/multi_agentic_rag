# Set base image (this loads the Debian Linux operating system)
FROM python:3.12
ENV PYTHONUNBUFFERED True

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV APP_HOME /root
COPY ./app $APP_HOME/app
COPY config.yaml $APP_HOME/config.yaml
WORKDIR $APP_HOME

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--timeout-keep-alive", "720"]