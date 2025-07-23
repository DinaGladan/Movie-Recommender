# nasa base image je python, koju smo uzeli s dockerhub-a (ima i drugih npr ubuntu)
FROM python:3.11-slim
WORKDIR /app
COPY . /app
#neka se instaliraju svi potrebni paketi koji su unutar file-a requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# pokretanje aplikacije
CMD ["python", "app.py"]
