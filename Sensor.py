import json
import random
from datetime import datetime
from LatestTelemetry import LatestTelemetry
from DataPacket import DataPacket
from Error_Messages import ErrorMessages
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
#controls

class Sensor:
    def __init__(self, sensor_id: str, label: str = None):
        self.sensor_id = sensor_id.strip().upper()
        self.label = label
        self.latestTelemetry = LatestTelemetry #boş başlatılmıştı

    def connected_to_module(self, module_id: str, gateway, topic):
        if not self.sensor_id:
            logger.error(ErrorMessages.SENSOR_ID_EMPTY.value)
            raise Exception(ErrorMessages.SENSOR_ID_EMPTY.value)

        self.create_telemetry()
        self.measure_all()

        if self.latestTelemetry is None:
            logger.error(ErrorMessages.TELEMETRY_NOT_PRODUCED.value)
            raise Exception(ErrorMessages.TELEMETRY_NOT_PRODUCED.value)

        telemetry_data = {
            "sensor_id": self.sensor_id,
            "timestamp": self.latestTelemetry["timestamp"],
            "o2": self.latestTelemetry["o2"],
            "co2": self.latestTelemetry["co2"],
            "temperature": self.latestTelemetry["temperature"],
            "rssi": self.latestTelemetry["rssi"]
        }

        try:
            with open("telemetry_log.txt", "r", encoding="utf-8") as file:
                data = json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            logger.warning(ErrorMessages.SENSOR_HAS_NO_TELEMETRY.value)
            data = []

        sensor_found = False
        for entry in data:
            if entry["sensor_id"] == self.sensor_id:
                entry["telemetry"].append(telemetry_data)
                sensor_found = True
                break

        if not sensor_found:
            data.append({
                "sensor_id": self.sensor_id,
                "telemetry": [telemetry_data]
            })
        self.create_telemetry()

    def create_telemetry(self):
        timestamp = datetime.now().isoformat()
        self.latestTelemetry = {
            "timestamp": timestamp,
            "o2": round(random.uniform(19.5, 21.0), 2),
            "co2": round(random.uniform(400, 600), 2),
            "temperature": round(random.uniform(22, 26), 2),
            "rssi": random.randint(-80, -40)
        }
        logger.debug("Telemetry başarıyla oluşturuldu.")

        # JSON formatına uygun şekilde telemetry_log.txt dosyasına yaz
        new_data = {
            "sensor_id": self.sensor_id,
            "telemetry": [self.latestTelemetry]
        }

        try:
            # Dosya yoksa veya boşsa sıfırdan başla
            with open("telemetry_log.txt", "r", encoding="utf-8") as file:
                existing_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []

        # Eğer aynı sensor_id varsa, ona yeni telemetry ekle
        for sensor in existing_data:
            if sensor["sensor_id"] == self.sensor_id:
                sensor["telemetry"].append(self.latestTelemetry)
                break
        else:
            # Yoksa yeni sensor_id ile ekle
            existing_data.append(new_data)

        with open("telemetry_log.txt", "w", encoding="utf-8") as file:
            json.dump(existing_data, file, indent=2, ensure_ascii=False)

        logger.debug(f"{self.sensor_id} sensörüne ait telemetry dosyaya kaydedildi.")

    def convert_to_datetime(self, timestamp: str):
        dt = datetime.fromisoformat(timestamp)
        return int(dt.timestamp() * 1000)

    def measure_all(self):
        try:
            with open("telemetry_log.txt", "r", encoding="utf-8") as file:
                data = json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            logger.warning(ErrorMessages.SENSOR_HAS_NO_TELEMETRY.value)
            data = []

        sensor_data = []
        for entry in data:
            if entry["sensor_id"] == self.sensor_id:
                sensor_data = entry["telemetry"]
                break

        if sensor_data:
            self.latestTelemetry = sensor_data[-1]
        else:
            self.latestTelemetry = None
            logger.warning(ErrorMessages.SENSOR_HAS_NO_TELEMETRY.value)

    def publish_telemetry(self, gateway, topic: str):
        if self.latestTelemetry is None:
            logger.warning("Önce ölçüm yapılmalı.")
            return

        logger.info(f"Sensor: {self.sensor_id} telemetry gönderdi.")
        logger.debug(self.latestTelemetry)

        packet = DataPacket(self.sensor_id, self.latestTelemetry)
        if gateway:
            gateway.onMqqtMessage(topic, packet)

