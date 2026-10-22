"""Send an example recommendation request to the Edu-Cater model server."""

import sys

import requests


MODEL_SERVER_URL = "http://127.0.0.1:8001/api/v1/recommend"
REQUEST_DATA = {
    "keam_rank": 500,
    "category": "bx",
    "courses": ["CS", "CY"],
    "types": ["government", "autonomous"],
}


def main() -> int:
    try:
        response = requests.post(MODEL_SERVER_URL, json=REQUEST_DATA, timeout=30)
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"Model server request failed: {error}", file=sys.stderr)
        return 1

    print(response.json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
