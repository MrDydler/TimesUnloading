import requests
from base64 import b64encode
import json
from datetime import datetime, timedelta
import postgres_cfg
from postgres_cfg import postgres

workspace_id = 5821463  # workspace_id

#Выгрузка пользователей
url_workspace = 'https://api.track.toggl.com/api/v9/organizations/5793735/workspaces/5821463/workspace_users'

workspaceData = requests.get(url_workspace, headers={'content-type': 'application/json', 'Authorization' : 'Basic %s' %  b64encode(b"a.gubashev@web-regata.ru:6891313881bB").decode("ascii")})
if workspaceData.status_code==200:
    #print("workspaceData = ", workspaceData.json())
    with open("toggleUsers.json", "w") as json_file:
        json.dump(workspaceData.json(), json_file, ensure_ascii=False, indent=2)
        print("Список пользователей сохранен в toggleusers.json")
else:
    print("ошибка запроса, код ", workspaceData.status_code)
    
#Выгрузка списка проектов    
url_projects = f'https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects'

projectData = requests.get(url_projects, headers={'content-type': 'application/json', 'Authorization' : 'Basic %s' %  b64encode(b"a.gubashev@web-regata.ru:6891313881bB").decode("ascii")})
if projectData.status_code==200:
    #print("workspaceData = ", workspaceData.json())
    with open("projectDataToggle.json", "w") as json_file:
        json.dump(projectData.json(), json_file, ensure_ascii=False, indent=2)
        print("Список проектов сохранен в toggleusers.json")
else:
    print("ошибка запроса, код ", projectData.status_code)

# загружаем имя клиента из projectDataToggle.json
with open("projectDataToggle.json", "r") as json_file:
    project_data = json.load(json_file)
    project_id_to_name = {str(project["id"]): project["name"] for project in project_data}
    print(project_id_to_name)

# параметры запроса
payload = {
    "end_date": "2023-08-30",
    "start_date": "2023-07-01",
    "grouped": False,
    "user_ids": [7185973, 8431059, 7819625, 9323244, 8738288, 8209137, 8829962, 7819625, 8431059, 9273122, 7032326],
    "order_by": "user",
    "first_row_number": 1  # стартутем с первой страницы
}

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {b64encode(b"a.gubashev@web-regata.ru:6891313881bB").decode("ascii")}'
}

all_time_entries = []

# цикл страниц (тоггл максимум выгружает 50 значений)
while True:
    response = requests.post(f'https://api.track.toggl.com/reports/api/v3/workspace/{workspace_id}/search/time_entries', json=payload, headers=headers)

    if response.status_code == 200:
        time_entries = response.json()
        #print('XXX_timeentries', time_entries)
        
        #из таймштампа
        filtered_entries = []
        for entry in time_entries:
            filtered_entry = {
                "user_id": entry["user_id"],
                "username": entry["username"],
                "project_id": entry["project_id"],
                "project_name": project_id_to_name.get(str(entry["project_id"]), ""),
                "billable": entry["billable"],
                "description": entry["description"],
                "time_entries": []
            }
            for time_entry in entry['time_entries']:
                start_timestamp = datetime.fromisoformat(time_entry['start'][:-6]) + timedelta(hours=5)
                stop_timestamp = datetime.fromisoformat(time_entry['stop'][:-6]) + timedelta(hours=5)
                time_entry['start'] = start_timestamp.strftime('%Y-%m-%d %H:%M:%S')
                time_entry['stop'] = stop_timestamp.strftime('%Y-%m-%d %H:%M:%S')
                del time_entry['at']  # удаляем 'at'
                
                seconds = time_entry['seconds']
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                normal_time = f"{hours:02d}:{minutes:02d}"
                time_entry['normal_time'] = normal_time
                
                filtered_entry['time_entries'].append(time_entry)
            filtered_entries.append(filtered_entry)
        
        all_time_entries.extend(filtered_entries)
        next_row_number = response.headers.get('X-Next-Row-Number')
        if next_row_number is None:
            break
        payload['first_row_number'] = int(next_row_number)  # Обновляем страницу следующим значением страницы
    else:
        print(f"Ошибка запроса, код: {response.status_code}")
        break

# запись в json
with open("report_toggle.json", "w") as json_file:
    json.dump(all_time_entries, json_file, ensure_ascii=False, indent=2)
    print("Таймеры сохранены в report_toggle.json")
    
    

 