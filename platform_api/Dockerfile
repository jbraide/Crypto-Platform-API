FROM python:3.9-slim
WORKDIR /app

COPY fixed-req.txt .
RUN pip install --no-cache-dir -r fixed-req.txt

COPY . .

EXPOSE 2500

CMD [ "python", "manage.py", "runserver", "0.0.0.0:2500" ]
