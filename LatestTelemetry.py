from datetime import datetime
import random

class LatestTelemetry():
    from datetime import datetime

    class LatestTelemetry:
        def __init__(self, timestamp, o2, co2, temp, rssi):
            self.timestamp = timestamp
            self.o2 = o2
            self.co2 = co2
            self.temp = temp
            self.rssi = rssi

        def __repr__(self):
            return f"Timestamp: {self.timestamp}, O2: {self.o2}, CO2: {self.co2}, Temp: {self.temp}, RSSI: {self.rssi}"

        #BU CLASS ARTIK SADECE OLUŞTURULUNCA KENDİNİ OTOMATİK OLARAK ÜRETİR
        #SENSOR BUNU İÇERİR YANİ SENSOR CLASSI İÇİNDE LASTTELEMETRY NESNESİ OLUŞTURULDU



