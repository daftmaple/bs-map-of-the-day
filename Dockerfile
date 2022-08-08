FROM python:3-alpine
WORKDIR /usr/src/app
COPY . .

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "src/app.py"]
