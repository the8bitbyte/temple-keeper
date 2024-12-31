import requests

def is_valid_username(username):
    try:
        url = f"https://auth.roblox.com/v1/usernames/validate?birthday=2006-09-21T07:00:00.000Z&context=Signup&username={username}"
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        return data.get("code") == 1
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return False

