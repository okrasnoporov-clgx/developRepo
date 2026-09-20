### PYTHON DEPENDENCIES

pip install "fastapi[standard]" 
pip install "pymongo"

### LOCAL RUN

python -m uvicorn service:app --host 0.0.0.0 --port 8000
# или:
python -m fastapi run .\service.py
python -m fastapi run .\service.py --host 0.0.0.0 --port 8000


### DOCKER CONTAINERIZATION

docker build --tag alpha-service:local .