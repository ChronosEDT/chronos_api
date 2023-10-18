import httpx


def get_client() -> httpx.AsyncClient:
    client = httpx.AsyncClient()

    client.headers.update(
        {"user-agent": "ChronosEDT/1.0.0"}
    )  # TODO: Use version in root __init__.py

    return client
