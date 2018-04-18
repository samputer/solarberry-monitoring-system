#!/usr/bin/env python
"""
                      \ | /
                    '-.;;;.-'
                   -==;;;;;==-
                    .-';;;'-.
                      / | \
                        '
 _____       _           ______
/  ___|     | |          | ___ \
\ `--.  ___ | | __ _ _ __| |_/ / ___ _ __ _ __ _   _
 `--. \/ _ \| |/ _` | '__| ___ \/ _ \ '__| '__| | | |
/\__/ / (_) | | (_| | |  | |_/ /  __/ |  | |  | |_| |
\____/ \___/|_|\__,_|_|  \____/ \___|_|  |_|   \__, |
Solarberry Monitoring System                    __/ |
by Sam Gray, 2018                              |___/

SolarBerry Monitoring System   Copyright (C) 2018  Sam Gray - www.sagray.co.uk

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
"""server.py

Usage:
  server.py [--demo] [--nolog] [--nosocket] [--nodb] [--websocketport=<port>] [--serialport=<port>] [--verbose]
  server.py (-h | --help)
  server.py --version
Options:
  -h --help     Show this screen.
  --version     Show version.
  --demo        Generate Sample Data instead of querying sensors
  --nolog       Do not log data into the database (default in demo mode)
  --nosocket    Do not broadcast data over the websocket connection
  --nodb        Do not use a database connection for configuration, use hardcoded values
  --websocketport=<port>  Websocket port [default: 5678].
  --serialport=<port>  Websocket port [default: /dev/ttyUSB0].
  --verbose     Very noisy! Useful for debugging
"""
from docopt import docopt
import datetime
import random
import json
import pymysql.cursors
import time
import serial
import signal, sys, ssl, logging, threading
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from collections import deque
import paramiko
from pymysql.converters import conversions, escape_datetime
import RPi.GPIO as GPIO



# global current_in
current_in = "0"
# global current_out
current_out = "0"
# global battery_percent_query_frequency
battery_percent_query_frequency = 10
# global battery_Ah
battery_Ah = 10000
# global battery_percent
battery_percent = 27
total_battery_Ah = 10000

shutdown_threshold = 70
calibration_voltage = 13.2
high_current_threshold = 70

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")

serialThreadLock = threading.Lock()
dbConnectionLock = threading.Lock()
initialDataCacheIsFull = False

def log(connection,metric,metricResult):
    with connection.cursor() as cursor:
      sql = "INSERT INTO "+metric['category']+" (`metric`, `value`,`level`) VALUES (%s,%s,%s)"
      with dbConnectionLock:
        cursor.execute(sql, (metric['name'],metricResult['value'],metricResult['level']))
        # print cursor._last_executed
        connection.commit()
        
def shutdown(ip=False,shutdownTime=60):
  targetIPs = []
  shutdownlist = '/home/pi/solar/solarberry-monitoring-system/Config/shutdownlist.txt'
  sshuser = 'pi'
  sshpass = 'raspberry'
  warningcommand = 'zenity -error -title="Low Battery" -text="Sorry, the SolarBerry is running low on battery power, this machine will shutdown in '+str(shutdownTime)+' second(s)"'
  shutdowncommand = 'sudo shutdown -P +'+str(shutdownTime)

  if (arguments['--demo']):
    print "\n**********************************WARNING******************************"
    print "THIS IS WHERE WE WOULD SHUTDOWN, BUT WE'RE IN DEMO MODE, SKIPPING THIS!"
    print "***********************************************************************\n"
  else:
    print "\n******WARNING******"
    print "Shutdown initiated!"
    print "*******************\n"
    if (ip):
      print "IP address was specified, shutting down "+ip
      targetIPs.append(ip)
    else:
      print "no IP was specified, shutting down all machines in the file"+ shutdownlist
      with open(shutdownlist) as f:
        targetIPs = f.readlines()
        targetIPs = [line.strip() for line in targetIPs] 
        f.close()
      ssh = paramiko.SSHClient()
      for ip in targetIPs:
        print '[Shutting down '+ip+' as user:'+sshuser+']:'
        fullcommand = warningcommand+'; '+shutdowncommand+';'
        print "Running: '",fullcommand,"'"
        try:
          ssh.connect(ip, username=sshuser, password=sshpass)
          ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(fullcommand)
          if (ssh_stdout | ssh_stderr):
            print ssh_stdout
            print ssh_stderr
        except Exception as e: # This is not great practice but I wasn't able to find the novalidconnectionserror exeption documented, so it'll do!
          print e
        print '\n'
    
def queryMetric(demoMode, metric, serialConnection, dbConnection):
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    value=''
    if(demoMode):
      if metric == 'graph1':
          # Take the most recent values of the values that we're interested in and return those (we're not strictly querying here, just rehashing old results)
          # Graph 2 we are interested in temperature and sunlight
          # This technically introduces a minor inaccuracy as it shows the time the message is sent, NOT the time the metric was captured
          # print(initialDataCache['irradiance'][-1]) # '-1' is funky python syntax for the last element in a list
          # print(initialDataCache['temperature_c'][-1]) # '-1' is funky python syntax for the last element in a list
  
          value = getGraph1Data(initialDataCache,dbConnection)
      else:
          value = round(random.uniform(0.0, 99.9),2)
    else:
        if metric in ['current_in','temperature_c','voltage_in','voltage_out','current_out','irradiance','battery_percent']:

            global current_in
            global current_out
            global battery_Ah
            global battery_percent_query_frequency
            global total_battery_Ah
            global battery_percent

            # If we know we need to get a specific value rather than random data, query the arduino for it
            with serialThreadLock:
                if metric == 'battery_percent':
                  serialConnection.write(str.encode('battery_percent_'+str(round(battery_percent,2))))
                else:
                  serialConnection.write(str.encode(metric))
                # time.sleep(1)
                # There could be a bunch of data coming back at any point, wait until we get our request
                foundResponse = 0
                failedAttemptCount = 0
                while(foundResponse == 0 and failedAttemptCount < 11):
                    response = serialConnection.readline()
                    # print "***"+response+"***"
                    if(metric in bytes.decode(response)):
                        foundResponse = 1
                        value = bytes.decode(response).split(":",1)[1].rstrip()
                        if metric in ['current_in','current_out']:
                      
                          if metric == 'current_in':
                            current_in = value
                          elif metric == 'current_out':
                            current_out = value
                          Ah_divisor = 3600/battery_percent_query_frequency
                          Ah_in = float(current_in)/Ah_divisor
                          Ah_out = float(current_out)/Ah_divisor
                          # print Ah_in
                          # print Ah_out
                          # print battery_Ah
                          battery_Ah = battery_Ah + Ah_in - Ah_out
                          battery_percent = float(100) / total_battery_Ah * battery_Ah
                          # print "Battery Percent***: "+str(int(battery_percent))

                    else:
                        failedAttemptCount += 1

        elif metric == 'battery_percent':
          value = battery_percent    
          # print "VALUE:"+str(battery_percent)
        elif metric == 'graph1':
          # See above (demo) for how this works - basically take the last snapshot of the metrics we care about
          value = getGraph1Data(initialDataCache,dbConnection)
          # print "*****"+str(value)+"*****"
        else:
            value = round(random.uniform(0.0, 99.9),2)
        return {'timestamp': now, 'value':value, 'level':getLevel(dbConnection,metric,value)}

def getLevel(connection,metric,value):
    if (arguments['--demo'] | arguments['--nodb'] ):
      # Obviously this has no bearing on the actual data being demo generated but its demo mode so we dont really care
      randIndex = random.randint(0,2)
      availableLevels = ["warning","danger","ok"]
      return availableLevels[randIndex]
    if (metric == 'graph1'):
      return 'Unknown'
    else:
      with connection.cursor() as cursor:
        #   # Read a single record
        # print metric
        # print value
        sql = "select level from thresholds where metric = %s and min <= %s and max > %s"
        with dbConnectionLock:
          cursor.execute(sql, (metric,value,value))
          result = cursor.fetchone()
      return result['level']

def getInitialData():
    print('sending initial data')
    initialDataCacheCopy = dict()
    for metric in initialDataCache:
      # print list(initialDataCache[metric])
      initialDataCacheCopy[metric] = json.dumps(list(initialDataCache[metric]))
    initialDataCacheCopy["initial"] = datetime.datetime.utcnow().isoformat() + 'Z'
    initialDataCacheCopy["config"] = metrics
    if (arguments['--verbose']):
      print str(json.dumps(initialDataCacheCopy))
    return str(json.dumps(initialDataCacheCopy))

def startWebsocketServer(server,int):
   # this only ever runs as a daemon, quietly sits there and handles our websocket stuff
   server.serveforever()

class DataBroadcast(WebSocket):

    def handleConnected(self):
        print(self.address, 'connected')

    def handleClose(self):
        print(self.address, 'closed')

    def handleMessage(self):
            if self.data is None:
                self.data = ''
            else:
                print("Received a message: ",str(self.data))
                received_json = json.loads(str(self.data))
                if 'ready' in received_json:
                  # We can send data now
                  self.sendMessage(str(getInitialData()))
                elif 'power' in received_json:
                  print "Received an instruction to control the power"
                  # We should turn the relay back on
                  # print received_json['power']
                  powerControl(received_json['power'])
                elif 'calibrate' in received_json:
                  print "Received an instruction to calibrate"
                  # We should turn the relay back on
                  # print received_json['power']
                  calibrate()
                else:
                  duration_received = received_json['duration']
                  method_received = received_json['method']
                  # metrics_received = received_json['metrics']
                  duration = ''
                  group_interval = ''
                  if (duration_received == 'year'):
                    duration = '1 year'
                    group_interval = 'year(timestamp),week(timestamp)'
                  elif (duration_received == 'month'):
                    duration = '1 month'
                    group_interval = 'year(timestamp),month(timestamp),day(timestamp)'
                  elif (duration_received == 'week'):
                    duration = '1 week'
                    group_interval = 'year(timestamp),month(timestamp),day(timestamp),hour(timestamp)'
                  elif (duration_received == 'day'):
                    duration = '1 day'
                    group_interval = 'year(timestamp),month(timestamp),day(timestamp),hour(timestamp)'

                  try:

                    # Create another db connection for this so we don't interfere with the periodic querying
                    dbConnection_demand = pymysql.connect(host='localhost',
                                 user='root',
                                 password='passw0rd!',
                                 db='solarberrydb',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
                    metrics = getMetrics(arguments,dbConnection_demand)

                    all_metric_json_results = list()

                    for metric in metrics:

                      # print metric['name']
                      # print metric
                      if (metric['name'] != "graph1"):
                        # sql = "SELECT `timestamp`, "+received_json['method']+"(`Value`) AS 'value' FROM `input` WHERE metric = 'voltage_in' AND timestamp > NOW() - INTERVAL "+duration+" GROUP BY "+group_interval+"(timestamp)"
                        sql = "SELECT `timestamp`, "+received_json['method']+"(`Value`) AS 'value' FROM "+metric['category']+" WHERE metric = '"+metric['name']+"' AND timestamp > NOW() - INTERVAL "+duration+" GROUP BY "+group_interval
                        print "GETTING REQUESTED DATA FOR "+metric['name']
                        print sql

                        with dbConnection_demand.cursor() as cursor:
                          cursor.execute(sql)
                          results = cursor.fetchall()

                          json_results = list()                    

                          for row in results:
                            current_row = dict()
                            current_row['timestamp'] = str(row['timestamp'])
                            current_row['value'] = float(row['value'])
                            current_row['metric'] = metric['name']
                            # json_results.append(current_row)

                            all_metric_json_results.append(current_row)


                    cursor.close()
                    dbConnection_demand.close() 

                    self.sendMessage(str(json.dumps({"response":datetime.datetime.utcnow().isoformat() 
                    + 'Z', "selected_method":received_json['method'], "selected_duration":received_json['duration'],
                    "SQL":json.dumps(all_metric_json_results)})))
                      
                  except Exception as e:
                    print e

def getConfigItem(item,dbConnection):
      connection = dbConnection
      with connection.cursor() as cursor:
          # Read a single record
        sql = "select value from config where name = %s"
        with dbConnectionLock:
          cursor.execute(sql, (item))
          result = cursor.fetchone()
          return result['value']


def doInitialConfig(arguments):

    # If we are in demo mode, we don't want to log this data to the db
    if(arguments['--demo']):
        arguments['--nolog'] = True
        print "--------------------------"
        print "***RUNNING IN DEMO MODE***"
        print "--------------------------"
        print "All data is generated and FAKE"
        print "No FAKE data will be logged"


    websocketServer = ''
    dbConnection = ''
    serialConnection = ''
    gpioConnection = ''

    # Sort out websockets if enabled...
    if(arguments['--nosocket'] == False):
        print "Creating a websocket connection..."
        cls = DataBroadcast # the class we're going to use
        websocketServer = SimpleWebSocketServer('', int(arguments['--websocketport']), cls)
        # This thread will run the websockets server
        # it handles all of the connected clients and deals with periodic broadcasting
        # sticking this in a thread allows us to continue doing the monitoring stuff without clients connected 
        # (which would just be silly and is how it briefly worked)
        print "Starting a thread to keep the websocket connection running..."
        t = threading.Thread(target=startWebsocketServer,args=(websocketServer,1))
        t.daemon = True
        t.start()
        def close_sig_handler(signal, frame):
            websocketServer.close()
            sys.exit()

        signal.signal(signal.SIGINT, close_sig_handler)

    else:
        print "WARNING - Websockets are disabled!!!"

    # Sort out database logging if enabled
    if(arguments['--nolog'] == False):
        print "Initialising database logging..."
        dbConnection = pymysql.connect(host='localhost',
                             user='root',
                             password='passw0rd!',
                             db='solarberrydb',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    else:
        print "WARNING - No data is being recorded to the database!!!"

    if(arguments['--demo'] == False):
        print "Setting up serial port connection..."
        serialConnection = serial.Serial(arguments['--serialport'], 9600) #9600 is the baud rate

        time.sleep(2)

        # Sending the init command to the arduino
        with serialThreadLock:
                serialConnection.write("init_10000_10_100");

    else:
        print "Running in DEMO mode - No need for a serial connection"


    # Setup the gpio to control the button
    # 18 is th button on the right side and 23 on the left
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(23, GPIO.IN,pull_up_down=GPIO.PUD_UP)

    # setup the gpio to control the relay
    GPIO.setup(21, GPIO.OUT)
    GPIO.output(21, GPIO.HIGH)

    # get some of our config items from the db
    global total_battery_Ah 
    total_battery_Ah = int(getConfigItem('battery_capacity',dbConnection))
    global calibration_voltage
    calibration_voltage = float(getConfigItem('calibrate_voltage_100_percent',dbConnection))
    global shutdown_threshold
    shutdown_threshold = int(getConfigItem('shutdown_threshold',dbConnection))
    global high_current_threshold
    high_current_threshold = int(getConfigItem('high_current_threshold',dbConnection))
    global battery_percent_query_frequency
    battery_percent_query_frequency = int(getConfigItem('battery_percent_query_frequency',dbConnection))


    return {'websocketServer': websocketServer, 'dbConnection': dbConnection, 'serialConnection':serialConnection}

def getMetrics(arguments,dbConnection):
    # Query the database for all the metrics we want to gather and how often we want to query them
    metrics = []
    #if we're in nodb mode - fake it 
    if (arguments['--nodb'] == False):
        connection = dbConnection
        print "Querying database for all metrics we need to gather"
        metrics = []
        with connection.cursor() as cursor:
          # Read a single record
          sql = "select name,category,frequency from poll_frequencies"
          with dbConnectionLock:
            cursor.execute(sql)
            result = cursor.fetchall()
            # print result
            metrics = result
    #     metrics = [{"name": "current_in",
    #            "category": "input",
    #            "frequency": 2},
    #            {"name": "voltage_in",
    #            "category": "input",
    #            "frequency": 2},
    #            {"name": "current_out",
    #            "category": "output",
    #            "frequency": 2},
    #            {"name": "voltage_out",
    #            "category": "output",
    #            "frequency": 5},
    #            {"name": "temperature_c",
    #            "category": "temperature",
    #            "frequency": 10},
    #            {"name": "battery_percent",
    #            "category": "battery",
    #            "frequency": 10},
    #            {"name": "irradiance",
    #            "category": "sun",
    #            "frequency": 2},
    #            {"name": "graph1",
    #            "category": "custom",
    #            "frequency":10}
    #            ]
    else:   
        print "Nodb was specified, we are going to use some default values for metrics instead"
        metrics = [{"name": "current_in",
               "category": "input",
               "frequency": 2},
               {"name": "voltage_in",
               "category": "input",
               "frequency": 2},
               {"name": "current_out",
               "category": "output",
               "frequency": 2},
               {"name": "voltage_out",
               "category": "output",
               "frequency": 5},
               {"name": "temperature_c",
               "category": "temperature",
               "frequency": 10},
               {"name": "battery_percent",
               "category": "battery",
               "frequency": 10},
               {"name": "irradiance",
               "category": "sun",
               "frequency": 2},
               {"name": "graph1",
               "category": "custom",
               "frequency":10}
               ]

    return metrics

def broadcast(metric,metricResult,server,arguments):
    # messageToSend = str(metric['name'])+' -> '+str(metricResult['value'])
    messageToSend = {'timestamp': metricResult['timestamp'], 'category':metric['category'], 'metric': metric['name'], 'value': metricResult['value'],'level':metricResult['level']}
    if (arguments['--verbose']):
        print "Sending '"+str(messageToSend)+"' to "+str(len(server.connections.values()))+" connected clients"
    for client in server.connections.values():
        client.sendMessage(json.dumps(messageToSend))

def getGraph1Data(initialDataCache,connection):
    if ((not initialDataCache['irradiance'])
      or(not initialDataCache['temperature_c'])
      or(not initialDataCache['current_in'])
      or(not initialDataCache['current_out'])
      or(not initialDataCache['voltage_in'])
      or(not initialDataCache['voltage_out'])
      or(not initialDataCache['battery_percent'])):
      # print len(initialDataCache['irradiance'])
      # print len(initialDataCache['temperature_c'])
      # print len(initialDataCache['current_in'])
      # print len(initialDataCache['current_out'])
      # print len(initialDataCache['voltage_in'])
      # print len(initialDataCache['voltage_out'])
      # print len(initialDataCache['battery_percent'])
      print "We don't have initialdatacache values for everything, using sample data"
      value = {'irradiance': {'timestamp':'2017-04-16 11:40:49', 'category':'sun', 'metric':'irradiance', 'value':'1','level':'ok'},
                       'temperature_c': {'timestamp':'2017-04-16 11:40:49', 'category':'temperature', 'metric':'temperature_c', 'value':'1','level':'ok'},
                       'current_in': {'timestamp':'2017-04-16 11:40:49', 'category':'input', 'metric':'current_in', 'value':'1','level':'ok'},
                       'current_out':{'timestamp':'2017-04-16 11:40:49', 'category':'output', 'metric':'current_out', 'value':'1','level':'ok'},
                       'voltage_in':{'timestamp':'2017-04-16 11:40:49', 'category':'input', 'metric':'voltage_in', 'value':'1','level':'ok'},
                       'voltage_out':{'timestamp':'2017-04-16 11:40:49', 'category':'output', 'metric':'voltage_out', 'value':'1','level':'ok'},
                       'battery_percent':{'timestamp':'2017-04-16 11:40:49', 'category':'battery', 'metric':'battery_percent', 'value':'1','level':'ok'}}
      return value

    else:
      # "Initial data cache is not empty"
      # print initialDataCache
      initialDataCacheIsFull = True
      value = {'irradiance': initialDataCache['irradiance'][-1],
                     'temperature_c':initialDataCache['temperature_c'][-1],
                     'current_in':initialDataCache['current_in'][-1],
                     'current_out':initialDataCache['current_out'][-1],
                     'voltage_in':initialDataCache['voltage_in'][-1],
                     'voltage_out':initialDataCache['voltage_out'][-1],
                     'battery_percent':initialDataCache['battery_percent'][-1]}
      return value
      # with connection.cursor() as cursor:
      #     # Read a single record
      #   sql = "select * from custom where metric = %s ORDER BY timestamp DESC LIMIT 1"
      #   with dbConnectionLock:
      #     cursor.execute(sql, ("graph1"))
      #     print(cursor._last_executed)
      #     result = cursor.fetchone()
      #     print "**********"
      #     print result['value']
      #     print "**********"
      #     value_result = json.dumps(result['value'])
      #     print value_result
      #     # # value = {'irradiance': result['irradiance'],
      #     #              'temperature_c':result['temperature_c'],
      #     #              'current_in':result['current_in'],
      #     #              'current_out':result['current_out'],
      #     #              'voltage_in':result['voltage_in'],
      #     #              'voltage_out':result['voltage_out'],
      #     #              'battery_percent':result['battery_percent']}


      #                sql = "select level from thresholds where metric = %s and min <= %s and max > %s"
      #   with dbConnectionLock:
      #     cursor.execute(sql, (metric,value,value))
      #     result = cursor.fetchone()
      # return result['level']


          # return value

def checkForRequiredActions(metric, metricResult, dbConnection):
  # This function will check if we need to do anything based on the value we just received
  if (initialDataCacheIsFull):
    if (metric['name'] == 'current_out' and metricResult >= high_current_threshold):
      # shutdown everything
      shutdown(None,10)
      powerControl(0)
    if (metric['name'] == 'battery_percent' and metricResult <= shutdown_threshold):
      shutdown(None,60)
      powerControl(0)
    if (metric['name'] == 'voltage_out' and metricResult > calibration_voltage):
      # This is the self-calibration, we can tell the Arduino that we're fully charged
      calibrate()

def calibrate():
  # We can currently only calibrate to 100%, which is convenient as passing multiple parameters to arduino is a PITA
  print "Calibrating to 100%"
  battery_Ah = total_battery_Ah
  battery_percent = 100

def powerControl(on):
  # Tell the arduino to shut off the relay that controls all the power
  if on:
    print "WARNING - Turning the SolarBerry power back on NOW!!!"
  else:
    print "WARNING - Shutting off all power to the Solarberry NOW!!!"
  
def checkForButtonPress():
  on = False
  while True:
    # this pin goes low when pushed
    if (GPIO.input(18) == 0):
      print "Button 1 pressed!"
      on = not on
      GPIO.output(21, on)
      powerControl(on)
      time.sleep(2) # add a small sleep so we don't trigger it twice
    if (GPIO.input(23) == 0):
      print "Button 2 pressed!"
      calibrate()
      time.sleep(2) # add a small sleep so we don't trigger it twice
    time.sleep(0.3)


def queryMetricContinuously(metric, connectionObjects, arguments,initialDataCache):
    # print metric['category']
    # print metric['name']
    # print metric['frequency']
    #This is the one that will be kicked off by a thread
    print "Beginning continuous query of "+metric['category']+" metric: *"+metric['name']+"* every "+str(metric['frequency'])+" seconds"
    time.sleep(1)
    while True:
        metricResult = queryMetric(arguments['--demo'], str(metric['name']), connectionObjects['serialConnection'], connectionObjects['dbConnection'])
        # checkForRequiredActions(metric, metricResult, connectionObjects['dbConnection'])
        initialDataCache[metric['name']].append(metricResult)
        if arguments['--nolog'] == False and metric['name'] != 'graph1':
            log(connectionObjects['dbConnection'],metric,metricResult)
        # if arguments['--nosocket'] == False:
        broadcast(metric,metricResult,connectionObjects['websocketServer'],arguments)
        time.sleep(metric['frequency'])

arguments = docopt(__doc__, version='server.py SolarBerry Monitoring System Version 1.0')

connectionObjects = doInitialConfig(arguments) # depending upon the parameters passed, this sets up the db connection and websockets
time.sleep(3) # Sleep for a couple of seconds after creating all of the communication objects, serial got upset without this

metrics = getMetrics(arguments,connectionObjects['dbConnection'])

# TODO - I should really be pulling this from the DB too
#  the numbers on the right control the size of the deque and therefore how many old snapshots we are pushing on init
initialDataCache = {
                    "current_in": deque([], 1),
                    "voltage_in": deque([], 1),
                    "current_out": deque([], 1),
                    "voltage_out": deque([], 1),
                    "temperature_c": deque([], 1),
                    "temperature_f": deque([], 1),
                    "battery_percent": deque([], 1),
                    "irradiance": deque([],1),
                    "graph1": deque([],50),
                    "graph2": deque([],50),
                    }
# Deque is a pretty awesome thing, allows more efficient management of queues

buttonThread = threading.Thread(target=checkForButtonPress)
buttonThread.daemon = True
buttonThread.start()

# For each of the metrics we get back, spin up a thread that continually queries the metric, does the neeful with the results and sleeps for the appropriate time
for metric in metrics:
    t = threading.Thread(target=queryMetricContinuously,args=(metric,connectionObjects,arguments,initialDataCache))
    t.daemon = True
    t.start()

# Now just keep an infinite loop going to confirm that the server is still going!
while True:
    now = datetime.datetime.utcnow().isoformat()
    print now,' - Server is still alive and kicking!'
    time.sleep(300)
