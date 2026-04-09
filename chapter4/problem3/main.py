import random
import threading
import time
from dataclasses import dataclass
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd

from db import create_database
from db import create_table
from db import get_sensor_count_and_hourly_average
from db import get_sensor_data
from db import insert_sensor_data


SENSOR_INTERVAL_SECONDS = 10
QUEUE_CHECK_INTERVAL_SECONDS = 1
AVERAGE_PRINT_INTERVAL_SECONDS = 300


@dataclass
class SensorRecord:
    sensor_name: str
    input_time: datetime
    temperature: int
    illuminance: int
    humidity: int


class ParmSensor:
    def __init__(self, sensor_name):
        self.sensor_name = sensor_name
        self.temperature = 0
        self.illuminance = 0
        self.humidity = 0
        self._lock = threading.Lock()

    def set_data(self):
        with self._lock:
            self.temperature = random.randint(20, 30)
            self.illuminance = random.randint(5000, 10000)
            self.humidity = random.randint(40, 70)

    def get_data(self):
        with self._lock:
            return self.temperature, self.illuminance, self.humidity


class SensorQueue:
    def __init__(self):
        self._items = []
        self._lock = threading.Lock()

    def enqueue(self, item):
        with self._lock:
            self._items.append(item)

    def dequeue(self):
        with self._lock:
            if not self._items:
                return None
            return self._items.pop(0)

    def is_empty(self):
        with self._lock:
            return len(self._items) == 0

    def size(self):
        with self._lock:
            return len(self._items)


sensorQ = SensorQueue()
memory_records = []
memory_records_lock = threading.Lock()


def print_sensor_record(record):
    timestamp = record.input_time.strftime('%Y-%m-%d %H:%M:%S')
    print(
        f'{timestamp} {record.sensor_name} - '
        f'temp {record.temperature}, '
        f'light {record.illuminance}, '
        f'humi {record.humidity}'
    )


def add_memory_record(record):
    with memory_records_lock:
        memory_records.append(
            {
                'sensor_name': record.sensor_name,
                'input_time': record.input_time,
                'temperature': record.temperature,
                'illuminance': record.illuminance,
                'humidity': record.humidity,
            }
        )


def print_five_minute_average():
    with memory_records_lock:
        if not memory_records:
            print('5분 평균 출력: 아직 수집된 데이터가 없습니다.')
            return

        df = pd.DataFrame(memory_records)

    df['input_time'] = pd.to_datetime(df['input_time'])
    df = df.sort_values('input_time')

    average_df = (
        df.groupby('sensor_name')
        .resample('5min', on='input_time')[['temperature', 'illuminance', 'humidity']]
        .mean()
        .round(2)
        .reset_index()
    )

    print('\n[5분 단위 평균 데이터]')
    print(average_df.to_string(index=False))
    print()


def sensor_worker(sensor, stop_event):
    while not stop_event.is_set():
        sensor.set_data()
        temperature, illuminance, humidity = sensor.get_data()

        record = SensorRecord(
            sensor_name=sensor.sensor_name,
            input_time=datetime.now(),
            temperature=temperature,
            illuminance=illuminance,
            humidity=humidity,
        )

        print_sensor_record(record)
        sensorQ.enqueue(record)
        add_memory_record(record)

        if stop_event.wait(SENSOR_INTERVAL_SECONDS):
            break


def queue_consumer_worker(stop_event):
    while not stop_event.is_set():
        time.sleep(QUEUE_CHECK_INTERVAL_SECONDS)

        while not sensorQ.is_empty():
            record = sensorQ.dequeue()

            if record is None:
                break

            insert_sensor_data(
                record.sensor_name,
                record.input_time.strftime('%Y-%m-%d %H:%M:%S'),
                record.temperature,
                record.illuminance,
                record.humidity,
            )

    while not sensorQ.is_empty():
        record = sensorQ.dequeue()

        if record is None:
            break

        insert_sensor_data(
            record.sensor_name,
            record.input_time.strftime('%Y-%m-%d %H:%M:%S'),
            record.temperature,
            record.illuminance,
            record.humidity,
        )


def average_report_worker(stop_event):
    while not stop_event.is_set():
        if stop_event.wait(AVERAGE_PRINT_INTERVAL_SECONDS):
            break
        print_five_minute_average()


def print_sensor_count_and_hourly_average():
    result_df = get_sensor_count_and_hourly_average()

    if result_df.empty:
        print('데이터베이스에 저장된 데이터가 없습니다.')
        return

    print('\n[센서별 데이터 개수 및 시간대 평균]')
    print(result_df.to_string(index=False))
    print()


def draw_hourly_temperature_graph():
    df = get_sensor_data()

    if df.empty:
        print('그래프를 그릴 데이터가 없습니다.')
        return

    df['input_time'] = pd.to_datetime(df['input_time'])
    df['hour'] = df['input_time'].dt.floor('h')

    hourly_temperature_df = (
        df.groupby(['sensor_name', 'hour'])['temperature']
        .mean()
        .reset_index()
    )

    plt.figure(figsize=(12, 6))

    for sensor_name, sensor_df in hourly_temperature_df.groupby('sensor_name'):
        plt.plot(
            sensor_df['hour'],
            sensor_df['temperature'],
            marker='o',
            label=sensor_name,
        )

    high_humidity_df = df[df['humidity'] > 90].copy()

    if not high_humidity_df.empty:
        high_humidity_df['hour'] = high_humidity_df['input_time'].dt.floor('h')

        highlight_df = pd.merge(
            high_humidity_df[['sensor_name', 'hour']].drop_duplicates(),
            hourly_temperature_df,
            on=['sensor_name', 'hour'],
            how='inner',
        )

        plt.scatter(
            highlight_df['hour'],
            highlight_df['temperature'],
            color='red',
            s=80,
            label='Humidity > 90',
            zorder=5,
        )

    plt.title('Average Hourly Temperature by Sensor')
    plt.xlabel('Hour')
    plt.ylabel('Average Temperature')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def main():
    create_database()
    create_table()

    sensors = [
        ParmSensor('Parm-1'),
        ParmSensor('Parm-2'),
        ParmSensor('Parm-3'),
        ParmSensor('Parm-4'),
        ParmSensor('Parm-5'),
    ]

    stop_event = threading.Event()
    threads = []

    for sensor in sensors:
        thread = threading.Thread(
            target=sensor_worker,
            args=(sensor, stop_event),
            daemon=True,
        )
        threads.append(thread)

    consumer_thread = threading.Thread(
        target=queue_consumer_worker,
        args=(stop_event,),
        daemon=True,
    )
    threads.append(consumer_thread)

    average_thread = threading.Thread(
        target=average_report_worker,
        args=(stop_event,),
        daemon=True,
    )
    threads.append(average_thread)

    for thread in threads:
        thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\n프로그램을 종료합니다...')
        stop_event.set()

        for thread in threads:
            thread.join(timeout=2)

        print_five_minute_average()
        print_sensor_count_and_hourly_average()
        draw_hourly_temperature_graph()


if __name__ == '__main__':
    main()