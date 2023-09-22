import requests
import json
from base64 import b64encode

organization_regata_id = 5793735
workspace_regata_id = 5821463


# response = requests.post(
#     'https://api.track.toggl.com/api/v9/me/sessions',
#     auth=('token', 'api_token'),
# )
# print(response.json())
# print("response_ANSWER ", response.status_code)


# if response.status_code == 200:
#     requests.get('https://api.track.toggl.com/api/v9/me/time_entries')
#     headers = {
#     'Content-Type': 'application/json',
# }

# response = requests.get('https://api.track.toggl.com/api/v9/me/time_entries', headers={'Content-Type': 'application/json', 'Authorization' : 'Basic %s' %  b64encode(b"login:password").decode("ascii")})
# #Обработка данных

# cards_data = response.json()
# required_data = []

#print("Time_entries_response ", response.json())
# print("Time_entries_response ", response.status_code)

# for card in cards_data:
#     space = card.get('workspace_id')
    
    
    #print("XX_space = ", space)


# with open("toggle.json", "w") as json_file:
#     json.dump(response.json(), json_file, ensure_ascii=False, indent=2)
    
    
    
url_workspace = 'https://api.track.toggl.com/api/v9/organizations/5793735/workspaces/5821463/workspace_users'

workspaceData = requests.get(url_workspace, headers={'content-type': 'application/json', 'Authorization' : 'Basic %s' %  b64encode(b"login:password").decode("ascii")})
#print("workspaceData = ", workspaceData.json())
with open("toggleUsers.json", "w") as json_file:
    json.dump(workspaceData.json(), json_file, ensure_ascii=False, indent=2)
    print("Список пользователей сохранен в toggleusers.json")


# workspace_info = requests.post('https://api.track.toggl.com/reports/api/v3/workspace/5821463/search/time_entries', headers={'Content-Type': 'application/json', 'Authorization' : 'Basic %s' %  b64encode(b"login:password").decode("ascii")})

# print("workspace_info", workspace_info.status_code)

# print(workspace_info.json())


# workspace_reports = requests.post('https://api.track.toggl.com/reports/api/v3/workspace/5821463/search/time_entries', json='{"billable":"false","end_date":"2023-08-28","start_date":"2023-08-01","grouped":"true","user_ids":["7185973","8431059", "7819625"], "order_by":"user",}', headers={'content-type': 'application/json', 'Authorization' : 'Basic %s' %  b64encode(b"login:password").decode("ascii")})

# print("workspace_reports", workspace_reports.status_code)

# print(workspace_reports.json())




#print("Workspace_info = " , workspace_info)


