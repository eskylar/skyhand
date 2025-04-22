import base64
import requests

#numbers stay the same jsut re run
CLIENT_ID = 'f8210b69869d406fb729f3547adf4a81'
CLIENT_SECRET = '15a4adb5758b471a8841cfc04dd8cfd0'
''

def get_spotify_token():
    auth_str = f'{CLIENT_ID}:{CLIENT_SECRET}'
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    token_url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': f'Basic {b64_auth_str}'
    }
    data = {
        'grant_type': 'client_credentials'
    }

    response = requests.post(token_url, headers=headers, data=data)

    if response.status_code != 200:
        print(f'Failed to get token: {response.status_code}')
        return None

    token_info = response.json()
    return token_info['access_token']

if __name__ == '__main__':
    token = get_spotify_token()
    if token:
        print('Your Spotify Access Token is:')
        print(token)
