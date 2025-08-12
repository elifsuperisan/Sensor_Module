import json
import os
import logging
from Sensor import Sensor
from Error_Messages import ErrorMessages

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Module:

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

    def connected_device(self, module_id, sensor_id):
        base_path = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_path, "dummy_data.txt")

        try:
            with open(file_path, 'r', encoding="utf-8") as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            logger.error(ErrorMessages.DUMMY_FILE_NOT_FOUND.value)
            return

        modules = data.get("modules", [])
        sensors = data.get("sensors", [])


         #checking the module/sensor ids paired it before or not
        matched_module = next((m for m in modules if m.get("module_id") == module_id), None)
        if not matched_module:
            logger.error(ErrorMessages.MODULE_NOT_FOUND.value)
            return
        elif matched_module.get("connectedSensor") is not None:
            logger.warning(ErrorMessages.MODULE_ALREADY_CONNECTED.value)
            return


        matched_sensor = next((s for s in sensors if s.get("sensor_id") == sensor_id), None)
        if not matched_sensor:
            logger.error(ErrorMessages.SENSOR_NOT_FOUND.value)
            return
        elif matched_sensor.get("label") is not None:
            logger.warning(ErrorMessages.SENSOR_ALREADY_CONNECTED.value)
            return

        #on thisblocks we're checkin the ids which are has the verified format but initally we pull the data by using get
        #and

        logger.info("Eşleşme yapılabilir, module ve sensor uygun durumda")
        #and then we created the verified module/sensor as an object

        sensor_obj = Sensor(sensor_id=matched_sensor["sensor_id"], label=None)
        sensor_obj.connected_to_module(module_id, gateway=None, topic="topic/test")

        matched_module["connectedSensor"] = sensor_id
        matched_sensor["label"] = module_id
        create_telemetry = sensor_obj.create_telemetry()
        try:
            with open(file_path, 'w', encoding="utf-8") as json_file:
                json.dump(data, json_file, indent=4, ensure_ascii=False)
                logger.info("Eşleşme dosyayı güncelledi.")
        except Exception as e:
            logger.error(f"Dosyaya yazım hatası: {e}")



        #indent=4 (Json'u okunabilir hale getirir)
        #ensure_ascii=False (Türkçe karakterler bozulmasın diye)

        # artık label----> module_id ve connected_device-----> sensor_id güncellemesi yap
        # belki bu güncellemeyi tekrar txt dosyasına geri yazıp ('w') dataları güncellemiş oluruz bu not olrk kalsın









