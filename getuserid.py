import requests

def get(username):
    url = "https://users.roblox.com/v1/usernames/users"
    payload = {"usernames": [username]}
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        if data["data"]:
            return data["data"][0]["id"]
        else:
            print(f"Username '{username}' not found.")
            return None
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None
