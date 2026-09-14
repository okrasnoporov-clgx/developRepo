import json
import os
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException


app = FastAPI()
info_endpoint = os.getenv("INFO_ENDPOINT", "/services/v1/info")
service_info_path = os.getenv("SERVICE_INFO_PATH", "/alpha/v1/info")


async def get_services_info() -> dict[str, Any]:
    try:
        services = json.loads(os.getenv("SERVICES", "[]"))
        if not isinstance(services, list) or any(
            not isinstance(service, dict) or not service.get("name") or not service.get("url")
            for service in services
        ):
            raise ValueError
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    timeout = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "5"))
    results = []
    async with httpx.AsyncClient(timeout=timeout) as client:
        for service in services:
            service_name = str(service["name"])
            service_url = str(service["url"]).rstrip("/")
            try:
                response = await client.get(f"{service_url}{service_info_path}")
                response.raise_for_status()
                results.append({"name": service_name, "status": "success", "response": response.json()})
            except (httpx.HTTPError, ValueError) as exc:
                results.append({"name": service_name, "status": "error", "error": str(exc)})

    return {"status": "success", "count": len(results), "services": results}


app.add_api_route(info_endpoint, get_services_info, methods=["GET"], tags=["Service info"])