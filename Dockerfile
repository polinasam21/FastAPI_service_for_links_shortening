FROM python:3.9

WORKDIR /proj

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /proj/app
COPY ./alembic.ini /proj/alembic.ini
COPY ./alembic /proj/alembic
