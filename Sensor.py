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
        if not self.sensor_id:
            logger.error(ErrorMessages.SENSOR_ID_EMPTY.value)
            raise Exception(ErrorMessages.SENSOR_ID_EMPTY.value)

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
            #dosya yoksa veya boşsa
            with open("telemetry_log.txt", "r", encoding="utf-8") as file:
                existing_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []

        # aynı sensor_id varsa ona bir daha yeni telemetry ekle
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

    def create_module(self):

        # base_path = os.path.dirname(os.path.abspath(__file__))
        # file_path = os.path.join(base_path, "dummy_data.txt")

        rand_sid = "S" + str(random.randint(0, 999999999)).zfill(9)
        # chat: rand_mid = "M" + " ".join(random.choice(string.ascii_uppercase + string.digits, k=7))

        while True:
            with open("dummy_data.txt", 'r', encoding="utf-8") as json_file:
                data = json.load(json_file)

            sensors = data.get("sensors", [])

            existing_ids = {m.get("sensor_id") for s in sensors if s.get("sensor_id")}

            if rand_sid in existing_ids:
                rand_sid = "S" + str(random.randint(0, 999999999)).zfill(9)
                continue
            else:
                break

        try:
            with open("dummy_data.txt", 'r', encoding="utf-8") as json_file:
                data = json.load(json_file)

        except FileNotFoundError:
            logger.error("Dummy_data.txt bulunamadı.")
            return
        except json.JSONDecodeError:
            logger.error("dummy_data.txt JSON formatı bozuk.")
            return

        # yeni kayıt for new ids
        new_sensors = {
            "sensor_id": rand_sid,
            "name": "Sensor" + rand_sid[-2:],
            "label": None
        }

        sensors.append(new_module)

        data["sensors"] = sensors  # yeniden eski modulelerin arasına ekledik

        try:
            with open("dummy_data.txt", 'w', encoding="utf-8") as json_file:
                json.dump(data, json_file, indent=4, ensure_ascii=False)
        except FileNotFoundError:
            logger.error("dummy_data.txt bulunamadı.");
            return
        except Exception as e:
            logger.error(f"Yazım hatası: {e}")
            return

        # yeniden dosyayı açıp dosyaya yazıldı mı diye kontrol et
        try:
            with open("dummy_data.txt", 'r', encoding="utf-8") as json_file:
                check_data = json.load(json_file)

                check_sensors = check_data.get("sensors", [])

                ok = any(m.get("sensor_id") == rand_sid for s in check_sensors)
                if ok:
                    logger.info("Doğrulama başarılı: sensor dosyaya eklendi.")
                    return {"message": "Sensor eklendi", "sensor_id": rand_sid}
                else:
                    logger.warning("Doğrulama başarısız: sensor dosyada bulunamadı.")
                    return

        except Exception as e:
            logger.error(f"Yazım hatası: {e}")
            return

    def main(self):
        module_id = input("Module ID girin: ").strip().upper()
        sensor_id = input("Sensor ID girin: ").strip().upper()

        if not module_id:
            logger.error(ErrorMessages.MODULE_ID_EMPTY.value)
            return

        if not sensor_id:
            logger.error(ErrorMessages.SENSOR_ID_EMPTY.value)
            return

        self.connected_device(module_id, sensor_id)


