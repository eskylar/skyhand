import base64
import requests

# 🔐 Replace these with your actual credentials
CLIENT_ID = '143397e589b24bb8947ab32600b76d90'
CLIENT_SECRET = '5b1729db0fdf49b5bb923c41853db9af'

def get_spotify_token():
    # Step 1: Encode client ID and secret
    auth_str = f'{CLIENT_ID}:{CLIENT_SECRET}'
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    # Step 2: Prepare POST request
    token_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f'Basic {b64_auth_str}'
    }
    data = {
        'grant_type': 'client_credentials'
    }

    # Step 3: Send request
    response = requests.post(token_url, headers=headers, data=data)

    if response.status_code != 200:
        print(f'Failed to get token: {response.status_code}')
        return None

    token_info = response.json()
    return token_info['access_token']

# Test it
if __name__ == '__main__':
    token = get_spotify_token()
    if token:
        print('Your Spotify Access Token is:')
        print(token)
