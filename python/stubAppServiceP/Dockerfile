FROM python:alpine3.23

WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir .

COPY service.py ./

EXPOSE 8000

CMD ["fastapi", "run", "service.py", "--host", "0.0.0.0", "--port", "8000"]
