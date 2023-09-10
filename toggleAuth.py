import requests
import json

response = requests.get('https://api.track.toggl.com/api/v9/me', auth=('a.gubashev@web-regata.ru', '6891313881bB'))
print(response.json())
