import irsdk
import time
import random 
from os import path
import yaml
from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server
totalRandomNumber = 0

# this is our State class, with some helpful variables
class State:
    ir_connected = False
    last_car_setup_tick = -1

class IracingMetricsCollector(object):
    def __init__(self):
        pass
    def collect(self):
        gauge = GaugeMetricFamily("random_number", "A random number generator, I have no better idea", labels=["randomNum"])
        gauge.add_metric(['random_num'], random.randint(1, 20))
        yield gauge
        count = CounterMetricFamily("random_number_2", "A random number 2.0", labels=['randomNum'])
        global totalRandomNumber
        totalRandomNumber += random.randint(1,30)
        count.add_metric(['random_num'], totalRandomNumber)
        yield count

# our main loop, where we retrieve data
# and do something useful with it
def loop():
    # on each tick we freeze buffer with live telemetry
    # it is optional, but useful if you use vars like CarIdxXXX
    # this way you will have consistent data from those vars inside one tick
    # because sometimes while you retrieve one CarIdxXXX variable
    # another one in next line of code could change
    # to the next iracing internal tick_count
    # and you will get incosistent data
    ir.freeze_var_buffer_latest()

    # retrieve live telemetry data
    # check here for list of available variables
    # https://github.com/kutu/pyirsdk/blob/master/vars.txt
    # this is not full list, because some cars has additional
    # specific variables, like break bias, wings adjustment, etc
    t = ir['SessionTime']
    print('session time:', t)

    # retrieve CarSetup from session data
    # we also check if CarSetup data has been updated
    # with ir.get_session_info_update_by_key(key)
    # but first you need to request data, before checking if its updated
    car_setup = ir['CarSetup']
    if car_setup:
        car_setup_tick = ir.get_session_info_update_by_key('CarSetup')
        if car_setup_tick != state.last_car_setup_tick:
            state.last_car_setup_tick = car_setup_tick
            print('car setup update count:', car_setup['UpdateCount'])
            # now you can go to garage, and do some changes with your setup
            # this line will be printed, only when you change something
            # and press apply button, but not every 1 sec
    # note about session info data
    # you should always check if data exists first
    # before do something like ir['WeekendInfo']['TeamRacing']
    # so do like this:
    # if ir['WeekendInfo']:
    #   print(ir['WeekendInfo']['TeamRacing'])
  


if __name__ == "__main__":
    ir = irsdk.IRSDK()
    state = State()

    port = 9000
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
        check_iracing()
        if state.ir_connected()
            loop()

            # period between collection
            time.sleep(frequency)
