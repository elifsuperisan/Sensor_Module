import logging
import json
import random
from os.path import exists

from flask import Flask, request, jsonify
from Gateway import Gateway
from Module import Module
from Sensor import Sensor
# from Error_Messages import Error_Messages

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

app = Flask(__name__)

@app.route("/connected_device", methods=["POST"])
def connected_device():
    data = request.get_json(silent=True) or {}
    module_id = (data.get("module_id") or "").strip().upper()
    sensor_id = (data.get("sensor_id") or "").strip().upper()

    if not module_id or not sensor_id:
        return jsonify({"error": "module_id and sensor_id are required"}), 400


    if not (module_id.startswith("M") and len(module_id) == 9 and module_id[1:].isdigit()):
        return jsonify({"error": "MODULE ID format is not valid"}), 400
    if not (sensor_id.startswith("S") and sensor_id[1:].isdigit() and len(sensor_id) in (5, 9)):
        return jsonify({"error": "SENSOR ID format is not valid"}), 400

    try:
        with open("dummy_data.txt", "r", encoding="utf-8") as f:
            data_file = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "Dummy data file not found"}), 500
    except json.JSONDecodeError:
        return jsonify({"error": "Dummy data file is corrupted"}), 500

    modules = data_file.get("modules", []) or []
    sensors = data_file.get("sensors", []) or []

    module = next((m for m in modules if isinstance(m, dict) and m.get("module_id") == module_id), None)
    sensor = next((s for s in sensors if isinstance(s, dict) and s.get("sensor_id") == sensor_id), None)
    if not module or not sensor:
        return jsonify({"error": "NOT_FOUND"}), 404

    if module.get("connectedSensor"):
        return jsonify({"error": "ALREADY_CONNECTED"}), 409
    if any(isinstance(m, dict) and m is not module and m.get("connectedSensor") == sensor_id for m in modules):
        return jsonify({"error": "ALREADY_CONNECTED"}), 409
    if (sensor.get("label") or "").strip():
        return jsonify({"error": "ALREADY_CONNECTED"}), 409

    module["connectedSensor"] = sensor_id
    sensor["label"] = module_id

    try:
        with open("dummy_data.txt", "w", encoding="utf-8") as f:
            json.dump(data_file, f, indent=4, ensure_ascii=False)
    except Exception:
        return jsonify({"error": "Could not save connection"}), 500

    # telemetry_loga ekliyoruz
    from datetime import datetime, timezone
    import random

    telemetry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "o2": round(random.uniform(19.0, 21.0), 2),
        "co2": round(random.uniform(420.0, 520.0), 2),
        "temperature": round(random.uniform(20.0, 28.0), 2),
        "rssi": random.randint(-80, -40)
    }

    try:
        with open("telemetry_log.txt", "r", encoding="utf-8") as f:
            log = json.load(f)
            if not isinstance(log, list):
                log = []
    except FileNotFoundError:
        log = []
    except json.JSONDecodeError:
        return jsonify({"error": "Telemetry log file is corrupted"}), 500

    #eşleşmiş sensor id var mı
    entry = next((e for e in log if e.get("sensor_id") == sensor_id), None)
    if entry is None:
        entry = {"sensor_id": sensor_id, "telemetry": []}
        log.append(entry)

    entry["telemetry"].append(telemetry)

    with open("telemetry_log.txt", "w", encoding="utf-8") as f:
        json.dump(log, f, indent=4)

    try:
        with open("telemetry_log.txt", "w", encoding="utf-8") as f:
            json.dump(log, f, indent=4, ensure_ascii=False)
    except Exception:
        return jsonify({"error": "Could not append telemetry"}), 500

    return jsonify({
        "connectedSensor": sensor_id,
        "label": module_id
    }), 200




@app.route("/create_module", methods=["POST"])
def create_module():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip().upper()

    if not name:
        logger.error("Module name is required")
        return jsonify({"error": "Module name is required"}), 400

    try:
        with open("dummy_data.txt", "r", encoding="utf-8") as file:
            data_file = json.load(file)
    except FileNotFoundError:
        logger.error("Dummy data file not found")
        return jsonify({"error": "Dummy data file not found"}), 500
    except json.JSONDecodeError:
        logger.error("Dummy data file is corrupted")
        return jsonify({"error": "Dummy data file is corrupted"}), 500

    modules = data_file.get("modules", [])
    if not isinstance(modules, list):
        modules = []
        data_file["modules"] = modules

    # aynı name engeli
    if any((m.get("name") or "").strip().upper() == name for m in modules):
        logger.error(f"Module name '{name}' already exists")
        return jsonify({"error": f"Module name '{name}' already exists"}), 409

    # ID üret ve çakışırsa yeniden üret
    rand_mid = "M" + str(random.randint(0, 99999999)).zfill(8)
    while any(m.get("module_id") == rand_mid for m in modules):
        rand_mid = "M" + str(random.randint(0, 99999999)).zfill(8)

    if not (rand_mid.startswith("M") and len(rand_mid) == 9 and rand_mid[1:].isdigit()):
        logger.error("MODULE ID FORMAT IS NOT VALID")
        return jsonify({"error": "Module ID format is not valid"}), 400

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

    return jsonify(new_module), 201




@app.route("/create_sensor", methods=["POST"])
def create_sensor():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip().upper()

    if not name:
        logger.error("Sensor name is required")
        return jsonify({"error": "Sensor name is required"}), 400

    try:
        with open("dummy_data.txt", "r", encoding="utf-8") as f:
            data_file = json.load(f)
    except FileNotFoundError:
        logger.error("Dummy data file not found")
        return jsonify({"error": "Dummy data file not found"}), 500
    except json.JSONDecodeError:
        logger.error("Dummy data file is corrupted")
        return jsonify({"error": "Dummy data file is corrupted"}), 500

    sensors = data_file.get("sensors", [])
    if not isinstance(sensors, list):
        sensors = []
        data_file["sensors"] = sensors

    # aynı name engeli
    if any((s.get("name") or "").strip().upper() == name for s in sensors):
        logger.error(f"Sensor name '{name}' already exists")
        return jsonify({"error": f"Sensor name '{name}' already exists"}), 409

    # ID üret ve çakışırsa yeniden üret
    rand_sid = "S" + str(random.randint(0, 99999999)).zfill(8)
    while any(s.get("sensor_id") == rand_sid for s in sensors):
        rand_sid = "S" + str(random.randint(0, 99999999)).zfill(8)

    if not (rand_sid.startswith("S") and len(rand_sid) == 9 and rand_sid[1:].isdigit()):
        logger.error("SENSOR ID FORMAT IS NOT VALID")
        return jsonify({"error": "Sensor ID format is not valid"}), 400

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

    return jsonify(new_sensor), 201






@app.route("/create_gateway", methods=["POST"])
def create_gateway():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip().upper()

    rand_gid = "G" + str(random.randint(0, 99999999)).zfill(8)

    if not (rand_gid.startswith("G") and len(rand_gid) == 9):
        logger.error("GATEWAY ID FORMAT IS NOT VALID")
        return jsonify({"error": "GATEWAY ID format is not valid"}), 400

    try:
        with open("dummy_data.txt", "r", encoding="utf-8") as file:
            data_file = json.load(file)
    except FileNotFoundError:
        logger.error("Dummy data file not found")
        return jsonify({"error": "Dummy data file not found"}), 500

    if not name:
        logger.error("GATEWAY NAME İS REQUİRED")
        return jsonify({"error": "Gateway name is required"}), 400

    try:
        with open("dummy_data.txt", "r", encoding="utf-8") as file:
            data_file = json.load(file)
    except FileNotFoundError:
        logger.error("Dummy data file not found")
        return jsonify({"error": "Dummy data file not found"}), 500

    gateways = data_file.get("gateways", [])

    # if name is already exist in the system  <-- just equeancy control (case-insensitive)
    if any((g.get("name") or "").strip().upper() == name for g in gateways):
        logger.error(f"Gateway '{name}' already exists")
        return jsonify({"error": f"Gateway '{name}' already exists"}), 400

    # duplicated state
    while any(g.get("gateway_id") == rand_gid for g in gateways):
        rand_gid = "G" + str(random.randint(0, 99999999)).zfill(8)

    new_gateway = {
        "gateway_id": rand_gid,
        "name": name
    }
    gateways.append(new_gateway)
    data_file["gateways"] = gateways

    try:
        with open("dummy_data.txt", "w", encoding="utf-8") as file:
            json.dump(data_file, file, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error writing to file: {e}")
        return jsonify({"error": "Could not save new gateway"}), 500

    response = {
        "gateway_id": rand_gid,
        "name": name,
        "success": "The new gateway has been successfully added"
    }
    return jsonify(response), 201



@app.route("/fetch_telemetry", methods=["POST"])
def fetch_telemetry():
    data = request.get_json(silent=True) or {}
    sensor_id = (data.get("sensor_id") or "").strip().upper()

    if data.get("sensor_id") is None:
        return jsonify({"error": "Sensor ID required"}), 400
    if not (sensor_id.startswith("S") and sensor_id[1:].isdigit() and len(sensor_id) in (5, 9)):
        return jsonify({"error": "SENSOR ID format is not valid"}), 400

    # telemetry_log oku
    try:
        with open("telemetry_log.txt", "r", encoding="utf-8") as f:
            log = json.load(f)
            if not isinstance(log, list):
                log = []
    except FileNotFoundError:
        log = []
    except json.JSONDecodeError:
        return jsonify({"error": "Telemetry log file is corrupted"}), 500

    entry = next((e for e in log if isinstance(e, dict) and e.get("sensor_id") == sensor_id), None)
    if not entry or not entry.get("telemetry"):
        return jsonify({"error": "This sensor_id has no telemetry packet"}), 404

    return jsonify({
        "sensor_id": sensor_id,
        "telemetry": entry.get("telemetry")
    }), 200




@app.route("/get_devices", methods=["POST"])
def get_devices():
    data = request.get_json(silent=True) or {}
    device_type = (data.get("device_type") or "").strip().lower()

    try:
        with open("dummy_data.txt", "r", encoding="utf-8") as f:
            dummy_data = json.load(f)
    except FileNotFoundError:
        logger.error("Dummy data file not found")
        return jsonify({"error": "Dummy data file not found"}), 500

    # if the device_type variable is none turn all of the lists
    if device_type == "":
        return jsonify({
            "gateways": dummy_data.get("gateways", []),
            "modules": dummy_data.get("modules", []),
            "sensors": dummy_data.get("sensors", [])
        }), 200

    if device_type not in dummy_data:
        return jsonify({"error": f"Device type '{device_type}' is not found"}), 404

    selected_type = dummy_data.get(device_type, [])

    # auto id sadece gateways için
    if device_type == "gateways":
        for g in selected_type:
            g["gateway_id"] = str(random.randint(0, 999_999_999)).zfill(9)

    # tüm device_type'lar için dosyadaki formatıyla döndür
    devices_out = selected_type

    with open("dummy_data.txt", "w", encoding="utf-8") as f:
        json.dump(dummy_data, f, indent=4, ensure_ascii=False)

    return jsonify({
        "device_type": device_type,
        "devices": devices_out
    }), 200






if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
                                                                                             