#!python3
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import time
import sys
from datetime import datetime
import signalfx
import irsdk
import argparse
import requests
from elasticsearch import Elasticsearch
import configparser



# Syntax:
# python3 iracing_send.py -name <YOUR_NAME_HERE> -token <YOUR_TOKEN_HERE> -i <YOUR_SPLUNK_ENTERPRISE_IP_HERE> -e <YOUR_SPLUNK_ENTERPRISE_HEC_TOKEN_HERE>
#
#parser = argparse.ArgumentParser(description="DataDrivers - iRacing Metric Sender")
#parser.add_argument("-n", "--name", help="Your iRacing Racer Name", required=True)
#parser.add_argument("-t", "--token", help="Splunk SIM Ingest Token", required=True)
#parser.add_argument("-i", "--ip", help="Splunk Enterprise IP Address", required=True)
#parser.add_argument("-e", "--enterprisetoken", help="Splunk Enterprise HEC Token", required=True)
#args = vars(parser.parse_args())

#################################
#   Change your variables here  #
#################################


name = input("Please enter your name: ")
team_name = input("Please enter your team name: ")

# SIM variables
sim_token = "Token"
client = signalfx.SignalFx(ingest_endpoint="https://ingest.us1.signalfx.com")
ingest = client.ingest(sim_token)

# Splunk enterprise variables
splunk_hec_ip = "IP"
splunk_hec_port = "8088"
splunk_hec_token = "Token"

#################################
# Don't touch anything below this#
#################################

# Uncomment the following line to enable debug logging
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# create dict for values of txt from github pyirsdk repo
# dictionary for metrics data

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
# dictionary for bool data
bool_dict = {
    "IsInGarage": "",
    "IsOnTrack": "",
    "IsOnTrackCar": "",
    "OnPitRoad": "",
    "PitstopActive": "",
    "PlayerCarInPitStall": "",
}

# this is our State class, with some helpful variables
class State:
    ir_connected = False
    last_car_setup_tick = -1


# Class used to track lap completions
class Counter:
    def __init__(self, count=1):
        self._count = count

    def get_count(self):
        return self._count

    def set_count(self, x):
        self._count = x

    count = property(get_count, set_count)


# here we check if we are connected to iracing
# so we can retrieve some data
def check_iracing():
    if state.ir_connected and not (ir.is_initialized and ir.is_connected):
        state.ir_connected = False
        # don't forget to reset your State variables
        state.last_car_setup_tick = -1
        # we are shutting down ir library (clearing all internal variables)
        ir.shutdown()
        print(datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " irsdk disconnected")
    elif (
        not state.ir_connected
        and ir.startup()
        and ir.is_initialized
        and ir.is_connected
    ):
        state.ir_connected = True
        print(datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " irsdk connected")


# Get current lap
def get_lap():
    return ir["Lap"]


# Sends event to SIM when lap is completed
def send_lap_event(counter):
    current_lap = int(get_lap())
    i = counter.count
    if current_lap == i:
        counter.count = current_lap + 1
        print(datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " new lap")
        ingest.send_event(
            event_type="Lap Complete",
            category="USER_DEFINED",
            dimensions={
                "driver": name,
                "TeamName": team_name,
                "lap": str(metrics_dict["Lap"]),
                "LapTime": str(metrics_dict["LapCurrentLapTime"]),
                "LapDistance": str(metrics_dict["LapDist"]),
            },
            properties={"session_id": str(metrics_dict["SessionUniqueID"])},
            timestamp=time.time() * 1000,
        )


# Sends metrics to SIM
def send_metric(ir_json):
    for key, value in ir_json.items():
        ingest.send(
            gauges=[
                {
                    "metric": "iracing." + key,
                    "value": value,
                    "timestamp": time.time() * 1000,
                    "dimensions": {
                        "driver": name,
                        "TeamName": team_name,
                        "lap": str(ir_json["Lap"]),
                        "session_id": str(ir_json["SessionUniqueID"]),
                    },
                }
            ]
        )

# function to send payload to splunk enterprise env
def send_hec(ir_json):
    ir_json['ts_send'] = str(datetime.utcnow())
    event={}
    event['host'] = name
    event['source'] = "iracing"
    event['time'] = int( time.time_ns() / 1000 )
    event['event'] = ir_json
    url = str("http://" + splunk_hec_ip + ":" + splunk_hec_port + "/services/collector")
    header = {'Authorization' : '{}'.format('Splunk ' + splunk_hec_token)}
    try:
        response = requests.post(
            url=url,
            data=json.dumps(event),
            headers=header)
        response.raise_for_status()

    except requests.exceptions.HTTPError as err:
        print(err)
        
def get_race_metadata():
    weekendinfo_meta={'TrackName' : "",
                 'TrackDisplayName' : "",
                 'TrackCity': "",
                 'TrackCountry': "",
                 'TrackID': "",
                 'TrackLength': "",
                 'TrackNumTurns': "",
                 'SeriesID': "",
                 'SeasonID': "",
                 'SessionID': "",
                 'SubSessionID': "",
                 'LeagueID': "",
                 'Official': "",
                 'RaceWeek': "",
                 'EventType': "",
                 'Category': ""}

    race_meta={}

    weekendinfo = ir['WeekendInfo']
    for key, value in weekendinfo_meta.items():
        value = weekendinfo[key]
        race_meta.update({key: value})

    driverinfo= ir['DriverInfo']
    race_meta.update({'DriverCarEngCylinderCount': driverinfo['DriverCarEngCylinderCount']})
    race_meta.update({'CarScreenName': driverinfo['Drivers'][0]['CarScreenName']})
    
    #Extract section start info, and determine the current sector
    
    current_sector = -1
    for sector in ir['SplitTimeInfo']['Sectors']:
        sector_count = sector["SectorNum"]
        if ir['LapDistPct'] > sector["SectorStartPct"]:
            current_sector = sector["SectorNum"]
        race_meta.update({"Sector_start_" + str(sector["SectorNum"]): sector["SectorStartPct"]})

    race_meta.update({"Sector_Count": sector_count + 1})
    race_meta.update({"Current_Sector": current_sector})
    
    return race_meta


def send_to_elk():
    client = Elasticsearch(
        cloud_id = ""
    )
    


def loop(json_dict):
    for key, value in json_dict.items():
        value = ir[key]
        json_dict.update({key: value})
        
    json_dict.update(get_race_metadata())
    json_dict.update({"@Timestamp": datetime.now()})

    try:
        # send_lap_event(lapCounter)
        pass
    except:
        print('error sending lap event.')
    try:
        pass
        # send_hec(json_dict)
        # with open('iracing.json', 'a') as f:
        #     json.dump(json_dict , f)

        # print(json_dict)
        send_to_elk(json_dict)
    except Exception as e:
        print(e)
        #print('error sending Splunk Enterprise payload.')
    try:
        pass
        # send_metric(json_dict)
    except:
        print('error sending o11y cloud payload.')


def send_to_elk(json_dict):

    config = configparser.ConfigParser()
    config.read('config.ini')

    es = Elasticsearch(
        cloud_id=config['ELASTIC']['cloud_id'],
        basic_auth=(config['ELASTIC']['user'], config['ELASTIC']['password'])
    )
    
    print(es.info())

    result = es.index(
        index = 'iracing-test-session',
        document = json_dict
    )


if __name__ == "__main__":
    # initializing ir and state
    ir = irsdk.IRSDK()
    state = State()
    print(datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " iRacing started")

    # instantiate lap counter for sending lap completion events
    lapCounter = Counter()
    ir.startup()

    # Update lap counter if iRacing is already running
    if ir.is_connected:
        lapCounter.count = ir["Lap"] + 1

    try:
        # infinite loop
        while True:
            # check if we are connected to iracing
            check_iracing()
            # if we are, then process data
            if state.ir_connected:
                loop(metrics_dict)
            print(
                datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                + " successfully looped through the script."
            )
            # sleep for 0.1 second
            # maximum you can use is 1/60 cause iracing updates data with 60 fps
            time.sleep(0.1)
    except KeyboardInterrupt:
        # press ctrl+c to exit
        pass
