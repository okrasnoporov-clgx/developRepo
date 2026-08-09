FROM python:3.13-slim

WORKDIR /app

# Install dependencies declared by the project before copying application code.
# This layer is reused while only service.py changes.
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

COPY service.py ./

EXPOSE 8000

CMD ["fastapi", "run", "service.py", "--host", "0.0.0.0", "--port", "8000"]
