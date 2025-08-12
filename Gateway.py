import json
from DataPacket import DataPacket

class Gateway:
    def __init__(self, gatewayId: str):
        self.gatewayId = gatewayId
        self.receivedDataPackets = []
        #take tl and appends to r list

    def onMqqtMessage(self, topic: str, packet: DataPacket):

        # when a tl packet comes over MQTT.
        self.receivedDataPackets.append(packet)
        print(f"Gateway {self.gatewayId} received a data packet from MQQT")
        print(f"Topic: {topic}")
        print(f"Sensor ID: {packet.sensor_id}")
        print(f"Telemetry: {packet.telemetry}")
        # adds the incoming packet to the receivedDataPackets list and pr

    def storeData(self):
        #writes the received telemetry data first collecting --->
        data_list = []
        for packet in self.receivedDataPackets:
            data = {
                "sensor_id": packet.sensor_id,
                "telemetry": packet.telemetry.__dict__ if hasattr(packet.telemetry, "__dict__") else packet.telemetry
                #telemetry nesnesinin tüm özelliklerini dict ile sözlük haline getiririz eğer dictse komple alırız appendle ekleriz
            }
            data_list.append(data)
            #to the gateway_data_log.txt file in JSON format.

        try:
            with open("gateway_data_log.txt", "w", encoding="utf-8") as file:
                json.dump(data_list, file, indent=4, ensure_ascii=False)
            print("Veriler başarıyla kaydedildi.")
        except Exception as e:
            print(f"Dosya kaydedilirken bir hata oluştu: {e}")

    def processData(self):

        #gateway_data_log.txt dosyasından verileri okur ve analiz etmeye hazır hale getirir.
        #Şimdilik sadece okuma kısmı vardır, ileride alarm üretme, analiz gibi işlevler eklenebilir.

        try:
            with open("gateway_data_log.txt", "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            print("Gateway data log dosyası bulunamadı.")
            return

        for entry in data:
            sensor_id = entry["sensor_id"] #current s_id
            telemetry = entry["telemetry"] # cr tl
            # Burada o2, co2, sıcaklık gibi telemetry bilgileri analiz edilebilir
            print(f"{sensor_id} The telemetry data from the sensor was examined.")


             # AKIŞ:
             # Sensor.connect_to_module() -----> measure_all() -----> latestTelemetry
             # DataPacket oluşturulur (sensor.latestTelemetry)
             # Gateway.onMqqtMessage() ile veri alınır
