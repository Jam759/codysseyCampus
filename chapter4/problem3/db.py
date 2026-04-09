import mysql.connector
import pandas as pd


MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'smart_farm_db',
}


def get_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)


def create_database():
    connection = mysql.connector.connect(
        host=MYSQL_CONFIG['host'],
        port=MYSQL_CONFIG['port'],
        user=MYSQL_CONFIG['user'],
        password=MYSQL_CONFIG['password'],
    )
    cursor = connection.cursor()

    cursor.execute(
        '''
        CREATE DATABASE IF NOT EXISTS smart_farm_db
        DEFAULT CHARACTER SET utf8mb4
        DEFAULT COLLATE utf8mb4_unicode_ci
        '''
    )

    connection.commit()
    cursor.close()
    connection.close()


def create_table():
    query = '''
        CREATE TABLE IF NOT EXISTS parm_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sensor_name VARCHAR(20) NOT NULL,
            input_time DATETIME NOT NULL,
            temperature INT NOT NULL,
            illuminance INT NOT NULL,
            humidity INT NOT NULL
        )
    '''

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()


def insert_sensor_data(sensor_name, input_time, temperature, illuminance, humidity):
    query = '''
        INSERT INTO parm_data (
            sensor_name,
            input_time,
            temperature,
            illuminance,
            humidity
        ) VALUES (%s, %s, %s, %s, %s)
    '''

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        query,
        (
            sensor_name,
            input_time,
            temperature,
            illuminance,
            humidity,
        ),
    )
    connection.commit()
    cursor.close()
    connection.close()


def get_sensor_data():
    query = '''
        SELECT
            id,
            sensor_name,
            input_time,
            temperature,
            illuminance,
            humidity
        FROM parm_data
        ORDER BY input_time
    '''

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    return pd.DataFrame(rows)


def get_sensor_count_and_hourly_average():
    query = '''
        SELECT
            sensor_name,
            COUNT(*) AS record_count,
            DATE_FORMAT(input_time, '%Y-%m-%d %H:00:00') AS hour_slot,
            ROUND(AVG(temperature), 2) AS avg_temperature,
            ROUND(AVG(illuminance), 2) AS avg_illuminance,
            ROUND(AVG(humidity), 2) AS avg_humidity
        FROM parm_data
        GROUP BY sensor_name, DATE_FORMAT(input_time, '%Y-%m-%d %H:00:00')
        ORDER BY sensor_name, hour_slot
    '''

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    return pd.DataFrame(rows)