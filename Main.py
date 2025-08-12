import json
import colorlog
import logging
import os
from Gateway import Gateway
from Sensor import Sensor
from Module import Module
from Error_Messages import ErrorMessages

#set up logging settings.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)s: %(message)s",
    log_colors={
        'DEBUG':    'white',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'bold_red',
    }
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

#with using file path for the checking there's any unexisting file
if not os.path.exists("gateway_data_log.txt"):
    with open("gateway_data_log.txt", "w", encoding="utf-8") as file:
        file.write("[]")

if not os.path.exists("telemetry_log.txt"):
    with open("telemetry_log.txt", "w", encoding="utf-8") as file:
        file.write("[]")

if not os.path.exists("dummy_data.txt"):
    logger.error(ErrorMessages.DUMMY_FILE_NOT_FOUND.value)
    exit()



def main():
    logger.info("Veri toplanıyor...")

    # get the ids from users
    module_id = input("Module ID giriniz: ").strip().upper()
    sensor_id = input("Sensor ID giriniz: ").strip().upper()


     #verified ids must be:
    if not module_id or not module_id.startswith("M") or len(module_id) != 5:
        logger.error(ErrorMessages.MODULE_ID_FORMAT_INVALID.value)


    if not sensor_id or not sensor_id.startswith("S") or len(sensor_id) != 5:
        logger.error(ErrorMessages.SENSOR_ID_FORMAT_INVALID.value)

    # if u... console would nt accept this type of entrys discarded from the system and never written to tele.


    # created objects
    gateway = Gateway(gatewayId="GW-001")
    sensor = Sensor(sensor_id=sensor_id)
    module = Module()
    topic = "sensor/telemetry"

    # matching with the modules
    module.connected_device(module_id, sensor_id)

    # sensor datas occurs in telemetry_log.txt and this func only calls
    #when ids true and if theres matching with dummy_data file
    sensor.connected_to_module(module_id, gateway, topic)

    # in additional if telemetry was produced it'll be published
    if sensor.latestTelemetry is not None:
        sensor.publish_telemetry(gateway, topic)
    else:
        logger.warning("It was not published because telemetry data was not reachable.")


if __name__ == "__main__":
    main()






