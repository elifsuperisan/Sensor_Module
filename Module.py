import json
import os
import logging
import random, string
from contextlib import nullcontext

from Sensor import Sensor
from Error_Messages import ErrorMessages

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Module:

    def connected_device(self, module_id, sensor_id):
        # Sensor class içindeki connected_to_module’de olan telemetry üretme + kaydetme kısmı

        base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_path, "dummy_data.txt")

        # doğru dosyayı mı test ediyor anlmaak için
        print("Kaydedilen dosya yolu:", file_path)

        try:
            with open(file_path, 'r', encoding="utf-8") as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            logger.error(ErrorMessages.DUMMY_FILE_NOT_FOUND.value)
            return  {"error": ErrorMessages.DUMMY_FILE_NOT_FOUND.value}

        modules = data.get("modules", [])
        sensors = data.get("sensors", [])

        # checking the module/sensor ids paired it before or not
        matched_module = next((m for m in modules if m.get("module_id") == module_id), None)
        if not matched_module:
            logger.error(ErrorMessages.MODULE_NOT_FOUND.value)
            return {"error": ErrorMessages.MODULE_NOT_FOUND.value}
        elif matched_module.get("connectedSensor") is not None:
            logger.warning(ErrorMessages.MODULE_ALREADY_CONNECTED.value)
            return {"error": ErrorMessages.MODULE_ALREADY_CONNECTED.value}

        matched_sensor = next((s for s in sensors if s.get("sensor_id") == sensor_id), None)
        if not matched_sensor:
            logger.error(ErrorMessages.SENSOR_NOT_FOUND.value)
            return {"error": ErrorMessages.SENSOR_NOT_FOUND.value}
        elif matched_sensor.get("label") is not None:
            logger.warning(ErrorMessages.SENSOR_ALREADY_CONNECTED.value)
            return {"error": ErrorMessages.SENSOR_ALREADY_CONNECTED.value}

        # on thisblocks we're checkin the ids which are has the verified format but initally we pull the data by using get

        logger.info("Eşleşme yapılabilir, module ve sensor uygun durumda")
        # and then we created the verified module/sensor as an object

        # Sıralama yanlışmış: önce JSON'u güncelle + yaz
        matched_module["connectedSensor"] = sensor_id
        matched_sensor["label"] = module_id

        try:
            with open(file_path, 'w', encoding="utf-8") as json_file:
                json.dump(data, json_file, indent=4, ensure_ascii=False)
                logger.info("Eşleşme dosyayı güncelledi.")
        except Exception as e:
            logger.error(f"Dosyaya yazım hatası: {e}")
            return {"error": f"Dosyaya yazım hatası: {e}"}

        sensor_obj = Sensor(sensor_id=matched_sensor["sensor_id"], label=None)
        sensor_obj.connected_to_module(module_id, gateway=None, topic="topic/test")


        # produce the telemetry and save it to the telemetry_log.txt file
        create_telemetry = sensor_obj.create_telemetry()

    # indent=4 (Json'u okunabilir hale getirir)
    # ensure_ascii=False (Türkçe karakterler bozulmasın diye)

    # artık label----> module_id ve connected_device-----> sensor_id güncellemesi yap
    # belki bu güncellemeyi tekrar txt dosyasına geri yazıp ('w') dataları güncellemiş oluruz bu not olrk kalsın

    def create_module(self):

        # base_path = os.path.dirname(os.path.abspath(__file__))
        # file_path = os.path.join(base_path, "dummy_data.txt")

        rand_mid = "M" + str(random.randint(0, 999999999)).zfill(9)
        # chat: rand_mid = "M" + " ".join(random.choice(string.ascii_uppercase + string.digits, k=7))

        while True:
            with open("dummy_data.txt", 'r', encoding="utf-8") as json_file:
                data = json.load(json_file)

            modules = data.get("modules", [])

            existing_ids = {m.get("module_id") for m in modules if m.get("module_id")}

            if rand_mid in existing_ids:
                rand_mid = "M" + str(random.randint(0, 999999999)).zfill(9)
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

        # new logs for new random ids to dummy's dicts as a list
        new_module = {
            "module_id": rand_mid,
            "name": "Module" + rand_mid[-2:],
            "connectedSensor": None
        }

        modules.append(new_module)

        data["modules"] = modules  # yeniden eski modulelerin arasına ekledik

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

                check_modules = check_data.get("modules", [])

                ok = any(m.get("module_id") == rand_mid for m in check_modules)
                if ok:
                    logger.info("Doğrulama başarılı: module dosyaya eklendi.")
                    return {"message": "Module eklendi", "module_id": rand_mid}
                else:
                    logger.warning("Doğrulama başarısız: module dosyada bulunamadı.")
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



