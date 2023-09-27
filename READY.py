import requests
from base64 import b64encode
import json
from datetime import datetime, timedelta
import time
from postgres_cfg import postgres_toggle, create_kaiten_times_table, create_data_kaiten_table
import psycopg2
from postgres_cfg import user, password, db_name, host, port
import configparser

from retrying import retry 

#configParser
config = configparser.ConfigParser()
config.read("config.txt")

toggle_login = config.get("DEFAULT", "toggle_login")
toggle_pass = config.get("DEFAULT", "toggle_pass")
api_key = config.get("DEFAULT", "api_key")
start_date = config.get("DEFAULT", "start_date")
end_date = config.get("DEFAULT", "end_date")

user_ids_str = config.get("DEFAULT", "user_ids")
user_ids = [int(id_str) for id_str in user_ids_str.split(',')]

print("toggle_login ", toggle_login)
print("toggle_pass ", toggle_pass)
print("api_key ", api_key)
print("start_date ", start_date)
print("end_date ", end_date)

host = config.get("POSTGRES", "host")
user = config.get("POSTGRES", "user")
password = config.get("POSTGRES", "password")
db_name = config.get("POSTGRES", "db_name")
port = config.get("POSTGRES", "port")


#Название таблиц, которые буду созданы в postgres и пути к json'ам
toggle_table_name = 'toggl'
report_toggle_path = 'report_toggle.json'

kaiten_data_tabble_name = 'kaiten_data'
kaiten_data_json_path = 'dataKaiten.json'

kaiten_times_tabble_name = 'kaiten_times'
kaiten_times_json_path = 'structured_time.json'


################################## TOGGLE #################################################################

#Выгрузка пользователей
workspace_id = 5821463  # workspace_id

#Выгрузка пользователей
url_workspace = 'https://api.track.toggl.com/api/v9/organizations/5793735/workspaces/5821463/workspace_users'

workspaceData = requests.get(url_workspace, headers={'content-type': 'application/json', 'Authorization' : 'Basic %s' %  b64encode(f"{toggle_login}:{toggle_pass}".encode("ascii")).decode("ascii")})
if workspaceData.status_code==200:
    #print("workspaceData = ", workspaceData.json())
    with open("toggleUsers.json", "w") as json_file:
        json.dump(workspaceData.json(), json_file, ensure_ascii=False, indent=2)
        print("Список пользователей сохранен в toggleusers.json")
else:
    print("ошибка запроса, код ", workspaceData.status_code)
    
#Выгрузка списка проектов    
url_projects = f'https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects'

projectData = requests.get(url_projects, headers={'content-type': 'application/json', 'Authorization' : 'Basic %s' %  b64encode(f"{toggle_login}:{toggle_pass}".encode("ascii")).decode("ascii")})
if projectData.status_code==200:
    #print("workspaceData = ", workspaceData.json())
    with open("projectDataToggle.json", "w") as json_file:
        json.dump(projectData.json(), json_file, ensure_ascii=False, indent=2)
        print("Список проектов toggle сохранен в projectDataToggle.json")
else:
    print("ошибка запроса toggle, код ", projectData.status_code)

# загружаем имя клиента из projectDataToggle.json
with open("projectDataToggle.json", "r") as json_file:
    project_data = json.load(json_file)
    project_id_to_name = {str(project["id"]): project["name"] for project in project_data}
    #print(project_id_to_name)

# параметры запроса
payload = {
    "start_date": f"{start_date}",
    "end_date": f"{end_date}",
    "grouped": False,
    "user_ids": user_ids,
    "order_by": "user",
    "first_row_number": 1  # стартутем с первой страницы
}
print(payload)

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic %s' %  b64encode(f"{toggle_login}:{toggle_pass}".encode("ascii")).decode("ascii")
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
                mins = seconds // 60
                time_entry['mins'] = mins
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
    
################################## /TOGGLE #################################################################


# ################################## KAITEN #################################################################
api_key = f"{api_key}"
api_url = "https://web-regata.kaiten.ru/api/latest/cards"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
#dataKaiten.json с общим списком карточек
response = requests.get(api_url, headers=headers)

if response.status_code == 200:
    try:
        cards_data = response.json()
        required_data = []

        # Move structured_data_with_totals initialization here
        structured_data_with_totals = {
            "time_logs_data": {},
            "total_time_per_card": {},
            "total_time_per_user": {}
        }

        for card in cards_data:
            space = card.get("space", {}).get("title", "N/A")
            property = card.get("properties", {})
            time_spent = card.get("time_spent_sum")
            if time_spent != 0:
                space_data = card.get("path_data", {}).get("space", {})
                space_title = space_data.get("title", "N/A")
                card_id = card.get("id")
                card_name = card.get("title")
                user_name = card.get("members")[0].get("full_name") if card.get("members") else ""
                user_email = card.get("members")[0].get("email") if card.get("members") else ""
                user_role = card.get("members")[0].get("username") if card.get("members") else ""
                comment = card.get("description")
                last_comment_date = card.get("last_comment_date")

                card_type = card.get("type", {}).get("name", "")

                amount_hours = card.get("amount_hours", 0)
                amount_minutes = card.get("amount_minutes", 0)
                time_spent2 = card.get("time_spent_sum", 0)

                # Рассчет часов и минут для time_spent
                spent_hours, spent_minutes = divmod(time_spent, 60)
                formatted_time_spent = f"{spent_hours:02}:{spent_minutes:02}"

                # Рассчет часов и минут для time_spent2
                spent2_hours, spent2_minutes = divmod(time_spent2, 60)
                formatted_time_spent2 = f"{spent2_hours:02}:{spent2_minutes:02}"

                required_data.append({
                    "Card ID": card_id,
                    "Card Name": card_name,
                    "User": user_name,
                    "User's Email": user_email,
                    "User Role": user_role,
                    "Comment": comment,
                    "Last Comment Date": last_comment_date,
                    "Property": property,
                    "Card Type": card_type,
                    "Space": space_title,
                    "Time_spent": time_spent2,
                    "Time_spent_with_hours": formatted_time_spent2
                })
                
                

        with open("dataKaiten.json", "w") as json_file:
            json.dump(required_data, json_file, ensure_ascii=False, indent=2)

        # for data in required_data:
        #     print("data =", data)

        print("Ответ 200")
        print("Выполнение скрипта ...")
    except Exception as e:
        print("ошибка декодинга json:", e)

else:
    print("Ошибка получения данных", response.status_code)
    print("Контент запроса:", response.text)

@retry(wait_fixed=2000, stop_max_attempt_number=5)
def get_card_time_logs(card_id):
    time_logs_url = f"https://web-regata.kaiten.ru/api/latest/cards/{card_id}/time-logs"
    response = requests.get(time_logs_url, headers=headers)
    
    if response.status_code == 200:
        time_logs_data = response.json()
        return time_logs_data
    elif response.status_code == 429:
        time.sleep(2)
        response = requests.get(time_logs_url, headers=headers)
        print("повторная отправка запроса", response.status_code)
        time_logs_data = response.json()
        return time_logs_data
    else:
        print(f"Ошибка при выборке журналов времени для карты {card_id}. Статус: {response.status_code}")
        response.raise_for_status()
        return []


# Загружаем айдишники из общей выгрузки карточек JSON file
with open("dataKaiten.json", "r") as json_file:
    cards_data = json.load(json_file)

time_logs_data = {}  # словарь time_logs_data

for card in cards_data:
    card_id = card["Card ID"]
    # получаем название клиента
    card_property = card.get("Property")  # Use .get() to safely handle None
    if card_property is not None and "id_181703" in card_property:
        custom_property_value = card_property["id_181703"][0]
        #print('custom_property_value ', custom_property_value)
        custom_property_url = f"https://web-regata.kaiten.ru/api/latest/company/custom-properties/{custom_property_value}/select-values/{custom_property_value}"
        response = requests.get(custom_property_url, headers=headers)
        if response.status_code == 200:
            try:
                customer_data = response.json()
                if customer_data is not None:
                    # Extract the "value" (Customer name) from the response
                    customer_name = customer_data.get("value", "N/A")
                    #print("customer_name ", customer_name)
                    # Add the "Customer" data to the time_logs_data
                    if card_id in time_logs_data:  # Make sure you're using time_logs_data here
                        if user_name in time_logs_data[card_id]:  # Make sure you're using time_logs_data here
                            time_logs_data[card_id][user_name]["Customer"] = customer_name
            except json.JSONDecodeError as e:
                print(f"Ошбика доступа к json data: {e}")

        elif response.status_code == 404:
            print(f"Выгрузка по карточке не удалась {custom_property_value}: {response.status_code}")
            #повторная отправка
        elif response.status_code == 429:
            time.sleep(1)
            response = requests.get(custom_property_url, headers=headers)
            print(f"повторная отправка запроса для {custom_property_value} отправка прошла с кодом {response.status_code}")
            try:
                customer_data = response.json()
                if customer_data is not None:
                    customer_name = customer_data.get("value", "N/A")
                    if card_id in time_logs_data:
                        if user_name in time_logs_data[card_id]:
                            time_logs_data[card_id][user_name]["Customer"] = customer_name
            except json.JSONDecodeError as e:
                print(f"Ошбика доступа к json data:: {e}")
        else:
            # Handle other potential errors
            print(f"Ошибка запроса {custom_property_value}: {response.status_code}")
            
                    
    time_logs = get_card_time_logs(card_id)
    
    for time_log in time_logs:
        user_name = time_log.get("author", {}).get("full_name")
        time_spent = time_log.get("time_spent")
        forDate = time_log.get("created")
        role = time_log.get("role", {}).get("name")#роль
        
        #print(forDate)
        
        
        
        if user_name is None or time_spent is None:
            print(f"Не нашел user_name или time_spent переменные в time_log:", time_log)
            continue
        
        if card_id not in time_logs_data:
            time_logs_data[card_id] = {}
        
        if user_name not in time_logs_data[card_id]:
            time_logs_data[card_id][user_name] = {
                "Time_spent": [],
                "Total_sum": 0,
                "Total_sum_with_hours": "00:00",
                "Role": role,
                "Customer": customer_name  
            }
        
        time_logs_data[card_id][user_name]["Time_spent"].append({
            "created": forDate,
            "time_spent": time_spent
        }) #заполнение времени

# расчет времени отдельнодля каждой карточки и юзера
total_time_per_card = {}
total_time_per_user = {}

for card_id, user_data in time_logs_data.items():
    for user_name, data in user_data.items():
        time_spent_list = data["Time_spent"]
        
        total_time = sum(entry["time_spent"] for entry in time_spent_list)  # Summing up time_spent values
        
        data["Total_sum"] = total_time
        
        # для пользователя
        total_hours, total_minutes = divmod(total_time, 60)
        formatted_total_time = f"{total_hours:02}:{total_minutes:02}"
        data["Total_sum_with_hours"] = formatted_total_time
        
        # Обновляем total_time для карточки
        if card_id not in total_time_per_card:
            total_time_per_card[card_id] = 0
        total_time_per_card[card_id] += total_time
        
        # обновляем total_time для юзера
        if user_name not in total_time_per_user:
            total_time_per_user[user_name] = 0
        total_time_per_user[user_name] += total_time

# структурно сохраняем в .json
structured_data_with_totals = {
    "time_logs_data": time_logs_data,
    "total_time_per_card": total_time_per_card,
    "total_time_per_user": total_time_per_user
}
for card_id, user_data in structured_data_with_totals["time_logs_data"].items():
    for user_name, data in user_data.items():
        time_spent_list = data["Time_spent"]
        for entry in time_spent_list:
            created_iso = entry["created"]
            created_iso = created_iso[:-1]  # удаляем 'Z' в конце, чтобы нормальночитался iso формат
            created_datetime = datetime.fromisoformat(created_iso)
            created_local = created_datetime + timedelta(hours=5)  # локальная дата
            formatted_created = created_local.strftime("%Y-%m-%d %H:%M:%S")
            entry["created"] = formatted_created

with open("structured_time.json", "w") as json_file:
    json.dump(structured_data_with_totals, json_file, ensure_ascii=False, indent=2)

print("Structured time logs data with totals saved to structured_time.json")



# ############################################################ KAITEN ###################################


############################### postgres ########################################################


try:
    connection = psycopg2.connect(host=host, port=port, user=user, password=password,dbname=db_name)
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        print(f"[INFO] Подключение к postgres успешно Server version: {cursor.fetchone()}")
        # cursor.execute("SELECT * FROM toggl;")
        # print(f"Table : {cursor.fetchall()}")
        
        postgres_toggle(report_toggle_path, toggle_table_name)
        print("postgres_toggle выполнено")
        
        create_kaiten_times_table(kaiten_times_tabble_name, kaiten_times_json_path)
        print("create_kaiten_times_table выполнено")
        
        create_data_kaiten_table(kaiten_data_tabble_name, kaiten_data_json_path)
        print("create_data_kaiten_table выполнено")
        
        
        pass
except Exception as _ex:
    print("[INFO] Ошибка подклчюения к postgres", _ex)
finally:
    if connection:
        connection.close()
        print("Соединение разорвано, выполнение успешно")
        input()