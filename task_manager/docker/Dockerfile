FROM python:3.12-alpine

WORKDIR /app

COPY /todo_requirements.txt /app

ENV PYTHONBUFFERED=1

RUN pip install --no-cache-dir --upgrade -r todo_requirements.txt

COPY . /app

CMD ["python3", "docker_persist.py"]