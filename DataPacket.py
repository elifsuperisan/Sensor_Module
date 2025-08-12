from LatestTelemetry import LatestTelemetry

class DataPacket:
    def __init__(self, sensor_id: str, telemetry: LatestTelemetry):
        self.sensor_id = sensor_id
        self.telemetry = telemetry


    #sensorden gelensensor_id ve latestTelemetryi alır



