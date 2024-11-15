# Verwenden Sie ein offizielles Python-Image als Basis
FROM python:3.9-slim

# Setzen Sie das Arbeitsverzeichnis im Container
WORKDIR /app

# Kopieren Sie die requirements.txt und installieren Sie die Abhängigkeiten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopieren Sie den Rest des Anwendungscodes
COPY . .

# Exponieren Sie den Port, auf dem die Anwendung läuft
EXPOSE 5000

# Starten Sie die Flask-Anwendung
CMD ["python", "app.py"]