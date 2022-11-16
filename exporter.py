import irsdk
import time
import random 
from os import path
import yaml
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily, InfoMetricFamily
from prometheus_client import start_http_server
totalRandomNumber = 0

metrics_dict = {
    "AirDensity": "",
    "AirPressure": "",
    "AirTemp": "",
    "BrakeRaw": "",
    "EngineWarnings": "",
    "FastRepairAvailable": "",
    "FastRepairUsed": "",
    "FogLevel": "",
    "FrameRate": "",
    "FuelLevel": "",
    "FuelLevelPct": "",
    "FuelUsePerHour": "",
    "Gear": "",
    "Lap": "",
    "LapBestLap": "",
    "LapBestLapTime": "",
    "LapCompleted": "",
    "LapCurrentLapTime": "",
    "LapDeltaToBestLap_DD": "",
    "LapDeltaToBestLap": "",
    "LapDeltaToOptimalLap_DD": "",
    "LapDeltaToOptimalLap": "",
    "LapDeltaToSessionBestLap_DD": "",
    "LapDeltaToSessionBestLap": "",
    "LapDeltaToSessionLastlLap_DD": "",
    "LapDeltaToSessionLastlLap": "",
    "LapDeltaToSessionOptimalLap_DD": "",
    "LapDeltaToSessionOptimalLap": "",
    "LapDist": "",
    "LapDistPct": "",
    "LapLasNLapSeq": "",
    "LapLastLapTime": "",
    "LapLastNLapTime": "",
    "LFtempCL": "",
    "LFtempCM": "",
    "LFtempCR": "",
    "LFwearL": "",
    "LFwearM": "",
    "LFwearR": "",
    "LRtempCL": "",
    "LRtempCM": "",
    "LRtempCR": "",
    "LRwearL": "",
    "LRwearM": "",
    "LRwearR": "",
    "OilLevel": "",
    "OilPress": "",
    "OilTemp": "",
    "PlayerCarClassPosition": "",
    "PlayerCarDriverIncidentCount": "",
    "PlayerCarIdx": "",
    "PlayerCarMyIncidentCount": "",
    "PlayerCarPosition": "",
    "PlayerCarTeamIncidentCount": "",
    "PlayerCarTowTime": "",
    "PlayerTireCompound": "",
    "PlayerTrackSurface": "",
    "PlayerTrackSurfaceMaterial": "",
    "RaceLaps": "",
    "RelativeHumidity": "",
    "RFtempCL": "",
    "RFtempCM": "",
    "RFtempCR": "",
    "RFwearL": "",
    "RFwearM": "",
    "RFwearR": "",
    "Roll": "",
    "RollRate": "",
    "RPM": "",
    "RRtempCL": "",
    "RRtempCM": "",
    "RRtempCR": "",
    "RRwearL": "",
    "RRwearM": "",
    "RRwearR": "",
    "SessionFlags": "",
    "SessionLapsRemain": "",
    "SessionNum": "",
    "SessionState": "",
    "SessionTime": "",
    "SessionTimeRemain": "",
    "SessionUniqueID": "",
    "ShiftGrindRPM": "",
    "ShiftIndicatorPct": "",
    "ShiftPowerPct": "",
    "Skies": "",
    "Speed": "",
    "SteeringWheelAngle": "",
    "SteeringWheelAngleMax": "",
    "SteeringWheelPctDamper": "",
    "SteeringWheelPctTorque": "",
    "SteeringWheelPctTorqueSign": "",
    "SteeringWheelPctTorqueSignStops": "",
    "SteeringWheelPeakForceNm": "",
    "SteeringWheelTorque": "",
    "ThrottleRaw": "",
    "TireSetsAvailable": "",
    "TireSetsUsed": "",
    "TrackTemp": "",
    "TrackTempCrew": "",
    "WeatherType": "",
    "WindDir": "",
    "WindVel": "",
    "@Timestamp": "",
}

# this is our State class, with some helpful variables
class State:
    ir_connected = False
    last_car_setup_tick = -1

class IracingMetricsCollector(object):

    def __init__(self):
        self.ir = irsdk.IRSDK()
        self.state = State()

    # here we check if we are connected to iracing
    # so we can retrieve some data
    def check_iracing(self):
        if self.state.ir_connected and not (self.ir.is_initialized and self.ir.is_connected):
            self.state.ir_connected = False
            # don't forget to reset your State variables
            self.state.last_car_setup_tick = -1
            # we are shutting down ir library (clearing all internal variables)
            self.ir.shutdown()
            print('irsdk disconnected')
        elif not self.state.ir_connected and self.ir.startup() and self.ir.is_initialized and self.ir.is_connected:
            self.state.ir_connected = True
            print('irsdk connected')       

    # our main loop, where we retrieve data
    # and do something useful with it
    def get_metrics(self, metrics_dict):
        # on each tick we freeze buffer with live telemetry
        # it is optional, but useful if you use vars like CarIdxXXX
        # this way you will have consistent data from those vars inside one tick
        # because sometimes while you retrieve one CarIdxXXX variable
        # another one in next line of code could change
        # to the next iracing internal tick_count
        # and you will get incosistent data
        self.ir.freeze_var_buffer_latest()

        print(self.ir['SessionInfo'])

        for key, value in metrics_dict.items():
            value = self.ir[key]

            metrics_dict.update({key: value})
        
        return metrics_dict


        # # retrieve live telemetry data
        # # check here for list of available variables
        # # https://github.com/kutu/pyirsdk/blob/master/vars.txt
        # # this is not full list, because some cars has additional
        # # specific variables, like break bias, wings adjustment, etc
        # t = self.ir['SessionTime']
        # fuel_level = ir['FuelLevel']
        # time_remaining = ir['SessionTimeRemain']
        # print('session time:', t)

        # # retrieve CarSetup from session data
        # # we also check if CarSetup data has been updated
        # # with ir.get_session_info_update_by_key(key)
        # # but first you need to request data, before checking if its updated
        # car_setup = ir['CarSetup']
        # if car_setup:
        #     car_setup_tick = ir.get_session_info_update_by_key('CarSetup')
        #     if car_setup_tick != state.last_car_setup_tick:
        #         state.last_car_setup_tick = car_setup_tick
        #         print('car setup update count:', car_setup['UpdateCount'])
        #         # now you can go to garage, and do some changes with your setup
        #         # this line will be printed, only when you change something
        #         # and press apply button, but not every 1 sec
        # # note about session info data
        # # you should always check if data exists first
        # # before do something like ir['WeekendInfo']['TeamRacing']
        # # so do like this:
        # # if ir['WeekendInfo']:
        # #   print(ir['WeekendInfo']['TeamRacing'])

    def collect(self):
        self.check_iracing()
        if self.state.ir_connected:
            metrics = self.get_metrics(metrics_dict)
            print(metrics)

            gauge = GaugeMetricFamily("fuel_level", "percentage of fuel available", labels=["fuel"])
            gauge.add_metric(['fuel_level'], metrics['FuelLevel'])
            yield gauge
            gauge = GaugeMetricFamily("time_remaining", "time remaining in the current sessions", labels=["time"])
            gauge.add_metric(['time_remaining'], metrics['SessionTimeRemain'])
            yield gauge
            gauge = GaugeMetricFamily("last_laptime", "last lap time", labels=["time"])
            gauge.add_metric(['last_laptime'], metrics['LapLastLapTime'])
            yield gauge
            gauge = GaugeMetricFamily("race_laps", "Laps completed in race", labels=["laps"])
            gauge.add_metric(['race_laps'], metrics['RaceLaps'])
            yield gauge            
            count = CounterMetricFamily("laps_completed", "number of laps completed", labels=['laps'])
            count.add_metric(['laps_completed'], metrics['LapCompleted'])
            yield count


if __name__ == "__main__":
    # ir = irsdk.IRSDK()
    # state = State()

    port = 9001
    frequency = 1
    if path.exists('config.yml'):
        with open('config.yml', 'r') as config_file:
            try:
                config = yaml.safe_load(config_file)
                port = int(config['port'])
                frequency = config['scrape_frequency']
            except yaml.YAMLError as error:
                print(error)

    start_http_server(port)
    REGISTRY.register(IracingMetricsCollector())
    while True: 
        # period between collection
        print("sleep")
        time.sleep(frequency)
