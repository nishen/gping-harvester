FROM python:3.12-slim-bullseye

WORKDIR /opt/gping-harvester
ADD Pipfile ./
ADD app.py ./

RUN pip install --no-cache-dir pipenv && pipenv install

CMD ["pipenv", "run", "launch"]
