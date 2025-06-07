FROM python:3.11-slim

WORKDIR /app

# Instala dependencias de sistema necesarias para Pillow, xhtml2pdf, pycairo, reportlab, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    pkg-config \
    libcairo2-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_APP=app.py

CMD ["python", "app.py"]
