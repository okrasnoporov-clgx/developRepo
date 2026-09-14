# Service information proxy

The service sends a `GET` request to the configured information endpoint of each configured service and returns all responses.

Environment variables:

- `SERVICES` - JSON array, for example `[{"name":"alpha","url":"https://alpha.example.com"},{"name":"beta","url":"https://beta.example.com"}]`.
- `SERVICE_INFO_PATH` - target path, default `/alpha/v1/info`.
- `INFO_ENDPOINT` - path exposed by this service, default `/services/v1/info`.
- `REQUEST_TIMEOUT_SECONDS` - request timeout in seconds, default `5`.

Run locally:

```text
fastapi run service.py
```