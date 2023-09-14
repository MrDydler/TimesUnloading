import requests
import json

response = requests.get('https://api.track.toggl.com/api/v9/me', auth=('log', 'pass'))
print(response.json())
