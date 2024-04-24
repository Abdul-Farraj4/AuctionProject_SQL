# 
# ITCS 3160-0002, Spring 2024
# Marco Vieira, marco.vieira@charlotte.edu
# University of North Carolina at Charlotte

from python:3.9-alpine

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

run pip install flask

run pip install psycopg2-binary

#copy . /app

#volume ["/app"]

workdir /app

# run mkdir -p logs

EXPOSE 5000

CMD ["python", "demo-proj.py"]
