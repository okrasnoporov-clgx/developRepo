# alpha-test-app

A minimal HTTP service for checking connectivity to a microservice in a cluster.
The `/` endpoint displays the application name and version in a colored table.
The `/v1/info` endpoint returns the same information as JSON.

| Environment variable | Default |
| --- | --- |
| `APP_NAME` | `alpha-test-app` |
| `APP_VERSION` | `v.0.0.1` |
| `PORT` | `8000` |

Run locally without a container (PowerShell):

```powershell
cd python\alpha-test-app
python app.py
```

Stop the service with `Ctrl+C` in the terminal where it is running.

To override the values before starting the app:

```powershell
$env:APP_NAME = "local-test"
$env:APP_VERSION = "v.1.2.3"
python app.py
```

In another terminal, open `http://localhost:8000/` or check the HTML response:

```powershell
Invoke-WebRequest http://localhost:8000/ | Select-Object -ExpandProperty Content
```

Check the JSON endpoint with:

```powershell
Invoke-RestMethod http://localhost:8000/v1/info
```

Build and run:

```sh
docker build -t alpha-test-app .
docker run --rm -p 8000:8000 \
  -e APP_NAME=alpha-test-app \
  -e APP_VERSION=v.0.0.1 \
  alpha-test-app
```

In Kubernetes, set `APP_NAME` and `APP_VERSION` from a ConfigMap as container
environment variables. The service listens on `0.0.0.0` and serves HTTP on port
`8000` by default.

The GitHub Actions workflow publishes the image to
`ghcr.io/<repository-owner>/alpha-test-app`, tagged with the version from
`pyproject.toml` and the commit SHA.
