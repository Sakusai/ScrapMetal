FROM python:3.12-bookworm

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps chromium

COPY . .

RUN useradd app
USER app

CMD ["python", "main.py"]