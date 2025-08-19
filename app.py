import logging
import json
import random

from flask import Flask, request, jsonify
from Module import Module
from Sensor import Sensor
# from Error_Messages import Error_Messages  # Kullanıyorsan aç

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

app = Flask(__name__)


@app.route("/connected_device", methods=["POST"])
def connected_device():
    data = request.get_json(silent=True) or {}
    module_id = (data.get("module_id") or "").strip().upper()
    sensor_id = (data.get("sensor_id") or "").strip().upper()

    @app.route("/connected_device", methods=["POST"])
    def connected_device():

        data = request.get_json(silent=True) or {}
        module_id = (data.get("module_id") or "").strip().upper()
        sensor_id = (data.get("sensor_id") or "").strip().upper()


        if not (module_id.startswith("M") and module_id[1:].isdigit() and len(module_id) <= 5):
            logger.error("INVALID_MODULE_ID")
            return jsonify({"error": "INVALID_MODULE_ID"}), 400
        if not (sensor_id.startswith("S") and sensor_id[1:].isdigit() and len(sensor_id) <= 5):
            logger.error("INVALID_SENSOR_ID")
            return jsonify({"error": "INVALID_SENSOR_ID"}), 400

        try:
            with open("dummy_data.txt", "r", encoding="utf-8") as file:
                data_file = json.load(file)
        except FileNotFoundError:
            logger.error("DUMMY_FILE_NOT_FOUND")
            return jsonify({"error": "DUMMY_FILE_NOT_FOUND"}), 500

        modules = data_file.get("modules", [])
        sensors = data_file.get("sensors", [])


        module_obj = next((m for m in modules if m.get("module_id") == module_id), None)
        if not module_obj:
            logger.error("MODULE_NOT_FOUND")
            return jsonify({"error": "MODULE_NOT_FOUND"}), 404

        sensor_obj = next((s for s in sensors if s.get("sensor_id") == sensor_id), None)
        if not sensor_obj:
            logger.error("SENSOR_NOT_FOUND")
            return jsonify({"error": "SENSOR_NOT_FOUND"}), 404

        if module_obj.get("connectedSensor") == sensor_id:
            logger.error("ALREADY_CONNECTED")
            return jsonify({"error": "ALREADY_CONNECTED"}), 400

        module_obj["connectedSensor"] = sensor_id

        try:
            with open("dummy_data.txt", "w", encoding="utf-8") as file:
                json.dump(data_file, file, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"WRITE_ERROR: {e}")
            return jsonify({"error": "WRITE_ERROR"}), 500

        # başarı = 200
        return jsonify({
            "module_id": module_id,
            "sensor_id": sensor_id,
            "success": "Module ve sensor başarıyla eşleştirildi."
        }), 200


@app.route("/create_module", methods=["POST"])
def create_module():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip().upper()

    rand_mid = "M" + str(random.randint(0, 99999999)).zfill(8)

    if not (rand_mid.startswith("M") and len(rand_mid) == 9):
        logger.error("MODULE ID FORMAT IS NOT VALID")
        return jsonify({"error": "Module ID format is not valid"}), 400

    try:
        with open("dummy_data.txt", "r", encoding="utf-8") as file:
            data_file = json.load(file)
    except FileNotFoundError:
        logger.error("Dummy data file not found")
        return jsonify({"error": "Dummy data file not found"}), 500

    modules = data_file.get("modules", [])

    if any(m.get("module_id") == rand_mid for m in modules):
        logger.error("Module ID already exists in the system")
        return jsonify({"error": "Module ID already exists"}), 400

    new_module = {
        "module_id": rand_mid,
        "name": name,
        "connectedSensor": None
    }
    modules.append(new_module)
    data_file["modules"] = modules

    try:
        with open("dummy_data.txt", "w", encoding="utf-8") as file:
            json.dump(data_file, file, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error writing to file: {e}")
        return jsonify({"error": "Could not save new module"}), 500

    response = {
        "module_id": rand_mid,
        "name": name,
        "connectedSensor": None,
        "success": "Yeni module başarıyla eklendi."
    }
    return jsonify(response), 201


@app.route("/create_sensor", methods=["POST"])
def create_sensor():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip().upper()

    rand_sid = "S" + str(random.randint(0, 99999999)).zfill(8)

    if not (rand_sid.startswith("S") and len(rand_sid) == 9):
        logger.error("SENSOR ID FORMAT IS NOT VALID")
        return jsonify({"error": "Sensor ID format is not valid"}), 400

    try:
        with open("dummy_data.txt", "r", encoding="utf-8") as f:
            data_file = json.load(f)
    except FileNotFoundError:
        logger.error("Dummy data file not found")
        return jsonify({"error": "Dummy data file not found"}), 500

    sensors = data_file.get("sensors", [])

    # (Opsiyonel) Şema normalize: "Label" → "label"
    for s in sensors:
        if "Label" in s and "label" not in s:
            s["label"] = s.pop("Label")

    if any(s.get("sensor_id") == rand_sid for s in sensors):
        logger.error("Sensor ID already exists in the system")
        return jsonify({"error": "Sensor ID already exists"}), 400

    new_sensor = {
        "sensor_id": rand_sid,
        "name": name,
        "label": None
    }
    sensors.append(new_sensor)
    data_file["sensors"] = sensors

    try:
        with open("dummy_data.txt", "w", encoding="utf-8") as f:
            json.dump(data_file, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error writing to file: {e}")
        return jsonify({"error": "Could not save new sensor"}), 500

    #başarı = 201
    response = {
        "sensor_id": rand_sid,
        "name": name,
        "label": None,
        "message": "Yeni sensor başarıyla eklendi."
    }
    return jsonify(response), 201


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)








