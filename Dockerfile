FROM python:3.11.3-slim-buster
WORKDIR /app
COPY modules ./modules
COPY processes ./processes
COPY config ./config
COPY *.py ./
COPY ninja_api_key ./
COPY requirements.txt .
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
EXPOSE 8000

CMD ["python", "main.py"]