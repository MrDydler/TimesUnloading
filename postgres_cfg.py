import psycopg2
import json
import configparser

#from READY import host,user,password,db_name,port
#configParser


config = configparser.ConfigParser()
config.read("config.txt")

host = config.get("POSTGRES", "host")
user = config.get("POSTGRES", "user")
password = config.get("POSTGRES", "password")
db_name = config.get("POSTGRES", "db_name")
port = config.get("POSTGRES", "port")

print(user)
print(host)
print(password)
print(db_name)
print(db_name)

# host = config.read("host
# user = "postgres"
# password = "1337"
# db_name = "postgres"
# port = 5433




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
        print(f'Таблица {kaiten_times_table_name} создана')

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


# kaiten_times_tabble_name = 'kaiten_times'
# kaiten_times_json_path = 'structured_time.json'
# create_kaiten_times_table(kaiten_times_tabble_name, kaiten_times_json_path)
    
#dataKaiten.json
def create_data_kaiten_table(kaiten_data_tabble_name, kaiten_data_json_path):
    connection = None
    cursor = None
    
    try:
        connection = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=db_name)
        cursor = connection.cursor()
        
        drop_sql = f"DROP TABLE IF EXISTS {kaiten_data_tabble_name} CASCADE"
        cursor.execute(drop_sql)
        connection.commit()
        
        create_sql = f"""
        CREATE TABLE {kaiten_data_tabble_name} (
            id SERIAL PRIMARY KEY,
            Card_id INTEGER,
            Card_Name TEXT,
            username NAME,
            User_email TEXT,
            User_role TEXT,
            comment TEXT,
            space TEXT,
            time INTEGER,
            Time_spent_with_hours TEXT
        )
        """
        cursor.execute(create_sql)
        print(f"Таблица {kaiten_data_tabble_name} создана")
        
        with open(kaiten_data_json_path, "r") as json_file:
            data_kaiten = json.load(json_file)
            
            for card_data in data_kaiten:
                card_id = card_data["Card ID"]
                card_name = card_data["Card Name"]
                username = card_data["User"]
                user_email = card_data["User's Email"]
                user_role = card_data["User Role"]
                comment = card_data["Comment"]
                space = card_data["Space"]
                time = card_data["Time_spent"]
                time_spent_with_hours = card_data["Time_spent_with_hours"]
                
                insert_sql = f"""
                INSERT INTO {kaiten_data_tabble_name} (Card_id, Card_Name, username, User_email, User_role, comment, space, time, Time_spent_with_hours)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (card_id, card_name, username, user_email, user_role, comment, space, time, time_spent_with_hours))
                connection.commit()
        
        print(f"{kaiten_data_tabble_name} таблица успешно создана в postgres")
        
    except Exception as ex:
        print("[INFO] Error connecting to PostgreSQL:", ex)
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("create_data_kaiten_table функция соединение закрыто")


# kaiten_data_tabble_name = "data_kaiten"
# kaiten_data_json_path = "dataKaiten.json"
# create_data_kaiten_table(kaiten_data_tabble_name, kaiten_data_json_path)
