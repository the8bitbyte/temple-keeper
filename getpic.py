import requests


def get_user_id(username):
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


def get_roblox_avatar_url(username):
    """
    Gets the avatar URL of a Roblox user by username.
    
    Args:
        username (str): The username of the Roblox user.
    
    Returns:
        str: The URL of the avatar picture, or an error message if unsuccessful.
    """
    try:
        # Step 1: Get user ID from username
        user_id = get_user_id(username)
        # Step 2: Get avatar picture URL
        avatar_url = f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=150x150&format=Png&isCircular=false"
        avatar_response = requests.get(avatar_url)
        avatar_data = avatar_response.json()
        
        if "data" in avatar_data and avatar_data["data"]:
            return avatar_data["data"][0]["imageUrl"]
        else:
            return "Avatar URL not found."
    
    except Exception as e:
        return f"An error occurred: {str(e)}"


