import requests

def get_age_guess(name: str) -> dict:
    url = "https://api.agify.io/"
    params = {"name": name}

    response = requests.get(url, params=params, timeout=5)
    response.raise_for_status()

    return response.json()
