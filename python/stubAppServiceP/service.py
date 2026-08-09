from fastapi import FastAPI

app = FastAPI()

@app.get("/alpha/v1/info", tags=["Service info"])
    
def get_info():
    return {"service": "alpha", "status": "ok", "server": "FastAPI"}
