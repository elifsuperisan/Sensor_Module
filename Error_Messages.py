from enum import Enum

class ErrorMessages(Enum): #errors that'll stop
    #logging red
    MODULE_ID_EMPTY = "Module ID can not be empty!"
    SENSOR_ID_EMPTY = "Sensor ID can not be empty!"
    MODULE_NOT_FOUND = "This module is not logged in system!"
    SENSOR_NOT_FOUND = "This sensor is not logged in system!"
    MODULE_ALREADY_CONNECTED = "This module is already matched!"
    SENSOR_ALREADY_CONNECTED = "This sensor is already matched!"
    TELEMETRY_NOT_PRODUCED = "Telemetry is not producted!"
    MODULE_ID_FORMAT_INVALID = "Module ID is invalid! Must starts with 'S' and has 5 digits!"
    SENSOR_ID_FORMAT_INVALID = "Sensor ID is invalid! Must starts with 'S' and has 5 digits!"

    #pushed the errors can be caused by while files read+save

    #yellow
    DUMMY_FILE_NOT_FOUND = "Dummy data file not found!"
    SENSOR_HAS_NO_TELEMETRY = "No telemetry data has been added for this sensor before."