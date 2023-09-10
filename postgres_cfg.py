host = "127.0.0.1"
user = "postgres"
password = "1337"
db_name = "test1"
port = 5432

import psycopg2
import json


def postgres_toggle(report_toggle_path, toggle_table_name):
    try:
        connection = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=db_name)
        print(f"Подклчение к таблице {toggle_table_name} выполнено")
        cursor = connection.cursor()
        
        # Удаляем предыдущую таблицу
        drop_sql = f"DROP TABLE IF EXISTS {toggle_table_name} CASCADE"
        cursor.execute(drop_sql)
        connection.commit()
        print(f'удаление таблицы {toggle_table_name} выполнено')
        
        create = f"""
        CREATE TABLE {toggle_table_name}
        (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    username NAME,
                    project_id INTEGER,
                    project_name TEXT,
                    description TEXT,
                    time_id BIGINT,
                    seconds INTEGER,
                    start_time TEXT,
                    stop_time TEXT,
                    normal_time TIME WITHOUT TIME ZONE
                    )
                    
                    """
        cursor.execute(create)
        connection.commit()
        print(f'Таблица {toggle_table_name} создана')

        with open(report_toggle_path, "r") as json_file:
            data = json.load(json_file)
            
            for entry in data:
                user_id = entry["user_id"]
                username = entry["username"]
                project_id = entry["project_id"]
                project_name = entry["project_name"]
                description = entry["description"]
                
                for times in entry["time_entries"]:
                    time_id = times["id"]
                    seconds = times["seconds"]
                    start_time = times["start"]
                    stop_time = times["stop"]
                    normal_time = times["normal_time"]
                    
                    #SQL INSERT
                    insert_sql = f"""
                    INSERT INTO {toggle_table_name} (user_id, username, project_id, project_name, description, time_id, seconds, start_time, stop_time, normal_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    # Исключение
                    cursor.execute(insert_sql, (user_id, username, project_id,project_name, description, time_id, seconds, start_time, stop_time, normal_time))
                    connection.commit()
                    
    except Exception as ex:
        print("[INFO] Error connecting to PostgreSQL:", ex)
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("Подключение к таблице postgres закрыто")

def create_kaiten_times_table(kaiten_times_table_name, kaiten_times_json_path):
    try:
        connection = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=db_name)
        cursor = connection.cursor()
        # Удаляем табилцу если существует в базе
        drop_sql = f"DROP TABLE IF EXISTS {kaiten_times_table_name} CASCADE"
        cursor.execute(drop_sql)
        connection.commit()
        
        # Создаем таблицу
        create_sql = f"""
        CREATE TABLE {kaiten_times_table_name} (
            id SERIAL PRIMARY KEY,
            card_id BIGINT,
            username NAME,
            time_spent INTEGER,
            total_sum_with_hours TEXT,
            role TEXT,
            customer TEXT,
            created TIMESTAMP,
            total_sum INTEGER
        )
        """

        cursor.execute(create_sql)
        print(f'Table {kaiten_times_table_name} created')

        # Читаем данные из джсона и заполняем (structured_time.json)
        with open(kaiten_times_json_path, "r") as json_file:
            structured_time_data = json.load(json_file)
            
            for card_id, card_data in structured_time_data["time_logs_data"].items():
                for username, user_data in card_data.items():
                    time_spent = user_data["Time_spent"][0]["time_spent"]
                    total_sum_with_hours = user_data["Total_sum_with_hours"]
                    role = user_data["Role"]
                    customer = user_data["Customer"]
                    created = user_data["Time_spent"][0]["created"]
                    total_sum = user_data["Total_sum"]
                
                    # SQL ISNERT 
                    insert_sql = f"""
                    INSERT INTO {kaiten_times_table_name} (card_id, username, time_spent, total_sum_with_hours, role, customer, created, total_sum)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    # исключение
                    cursor.execute(insert_sql, (card_id, username, time_spent, total_sum_with_hours, role, customer, created, total_sum))
        
        connection.commit()
        print("Data_kaiten таблица успешно создана в postgres")
        
    except Exception as ex:
        print("[INFO] Error connecting to PostgreSQL:", ex)
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("create_kaiten_times_table соединение закрыто")


kaiten_times_tabble_name = 'kaiten_times'
kaiten_times_json_path = 'structured_time.json'
create_kaiten_times_table(kaiten_times_tabble_name, kaiten_times_json_path)
    


