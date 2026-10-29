# beta-test-app

A minimal HTTP service for checking connectivity to another microservice in a
cluster. The `/` endpoint displays the application name and version in a table.
The `/v1/info` endpoint returns its own information as JSON, and
`/v1/alpha/info` returns the JSON response from the alpha service's `/v1/info`
endpoint.

| Environment variable | Default |
| --- | --- |
| `APP_NAME` | `beta-test-app` |
| `APP_VERSION` | `v.0.0.1` |
| `PORT` | `8000` |
| `SVC` | `alpha-test-app` |

`SVC` is the DNS name of the alpha service. Beta requests
`http://<SVC>:8000/v1/info` with a five-second timeout.

Run locally without a container (PowerShell):

```powershell
cd python\mesh-istio-test-bg\beta-test-app
$env:PORT = "8001"
$env:SVC = "localhost"
python app.py
```

In another terminal, open `http://localhost:8001/`, check beta's
`http://localhost:8001/v1/info`, or proxy alpha's information with
`http://localhost:8001/v1/alpha/info`. This example expects alpha to be running
on port `8000`.

Build and run:

```sh
docker build -t beta-test-app .
docker run --rm -p 8000:8000 \
  -e APP_NAME=beta-test-app \
  -e APP_VERSION=v.0.0.1 \
  -e SVC=alpha-test-app \
  beta-test-app
```

In Kubernetes, set `SVC` to the alpha service DNS name and set `APP_NAME` and
`APP_VERSION` from a ConfigMap as container environment variables. The service
listens on `0.0.0.0` and serves HTTP on port `8000` by default. If the alpha
service cannot be reached, `/v1/alpha/info` returns HTTP `502`.

The GitHub Actions workflow publishes the image to
`ghcr.io/<repository-owner>/beta-test-app`, tagged with the version from
`pyproject.toml` and the commit SHA.
