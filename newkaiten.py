from datetime import datetime, timedelta
import requests
import json

api_key = "d02df52b-a67e-4971-a0fd-b57ead3718c5"
api_url = "https://web-regata.kaiten.ru/api/latest/cards"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

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

        for data in required_data:
            print("data =", data)

        print("Ответ 200")

    except Exception as e:
        print("ошибка декодинга json:", e)

else:
    print("Ошибка получения данных", response.status_code)
    print("Контент запроса:", response.text)


def get_card_time_logs(card_id):
    time_logs_url = f"https://web-regata.kaiten.ru/api/latest/cards/{card_id}/time-logs"
    response = requests.get(time_logs_url, headers=headers)
    
    if response.status_code == 200:
        time_logs_data = response.json()
        return time_logs_data
    else:
        print(f"Ошибка при выборке журналов времени для карты {card_id}. Статус: {response.status_code}")
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
                print(f"Error decoding JSON response for customer data: {e}")

        elif response.status_code == 404:
            print(f"Customer data not found for property value {custom_property_value}: {response.status_code}")
        else:
            # Handle other potential errors
            print(f"Error fetching customer data for property value {custom_property_value}: {response.status_code}")
            
                    
    time_logs = get_card_time_logs(card_id)
    
    for time_log in time_logs:
        user_name = time_log.get("author", {}).get("full_name")
        time_spent = time_log.get("time_spent")
        forDate = time_log.get("created")
        role = time_log.get("role", {}).get("name")#роль
        
        #print(forDate)
        
        
        
        if user_name is None or time_spent is None:
            print(f"Missing user_name or time_spent data in time_log:", time_log)
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

print("Structured time logs data with totals saved to structured_time.json")#, json.dumps(structured_data_with_totals, ensure_ascii=False, indent=2)