/*
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

*/

#include <OneWire.h>
#include <DallasTemperature.h>
#include <LiquidCrystal.h>
#include <TimedAction.h>
#include <Wire.h>
#include <Adafruit_INA219.h>
#include<stdbool.h>
#include <string.h>



// See https://cdn-learn.adafruit.com/downloads/pdf/adafruit-ina219-current-sensor-breakout.pdf for jumper config



Adafruit_INA219 ina219_in(0x41); // A0 shorted
Adafruit_INA219 ina219_out(0x44); // A1 shorted
Adafruit_INA219 ina219_batt(0x40); // A0 & A1 shorted

#define CURRENT_BATTERY 0
#define CURRENT_IN 1
#define TEMPERATURE_C 2
#define VOLTAGE_IN 3
#define BATTERY_PERCENT 4
#define VOLTAGE_OUT 5
#define CURRENT_OUT 6
#define VOLTAGE_BATTERY 7

// ***** PIN DEFINITIONS *****
// RGB LED
int redPin = 9;
int greenPin = 10;
int bluePin =11;
// LCD Pins
int LCDPin1 = 7;
int LCDPin2 = 6;
int LCDPin3 = 5;
int LCDPin4 = 4;
int LCDPin5 = 3;
int LCDPin6 = 2;
// OneWire Pin (thermometer)
int OneWirePin = 8;

// Relay
int relayPin = 12;

// List of all metrics, their default values, names and units
String metrics[8] = {"???", "???", "???", "???", "???", "???", "???", "???"};
String metricnames[8] = {"Curr Batt","Curr in", "Temp", "V in", "Batt %", "Batt V", "Curr out", "Batt V"};
String metricunits[8] = {"A", "A", "\337C", "V", "%", "V", "A", "V"};

int lastDisplayedOnScreen = 0;

String in = "none";         // incoming serial byte
LiquidCrystal lcd(LCDPin1,LCDPin2,LCDPin3,LCDPin4,LCDPin5,LCDPin6);

// Setup a oneWire instance to communicate with any OneWire devices (not just Maxim/Dallas temperature ICs)
OneWire oneWire(OneWirePin);

// Pass our oneWire reference to Dallas Temperature.;;;
DallasTemperature oneWireSensors(&oneWire);

// Define all of our metric variables
//String temperature_c;
String temperature_f;
//String current_in;
float battery_percent;
int total_battery_Ah;
int battery_Ah;
int battery_percent_query_frequency = 10; // TODO pull this from the initial config
bool readytoroll = false;

void updateScreen() {
  if(readytoroll){
  lcd.noBlink();
  lcd.setCursor(0, 1);
  String message = metricnames[lastDisplayedOnScreen] + ": " + metrics[lastDisplayedOnScreen] + metricunits[lastDisplayedOnScreen];
  int numberOfSpaces = 16 - (message.length());
  int numberOfSpacesBefore = 0;
  int numberOfSpacesAfter = 0;
  if (numberOfSpaces > 1) {
    numberOfSpacesBefore = (int)numberOfSpaces / 2;
    numberOfSpacesAfter = (int)numberOfSpaces / 2;
    for (int i = 0; i < numberOfSpacesBefore; i++) {message = " " + message;}
    for (int i = 0; i <= numberOfSpacesAfter; i++) {message = message + " ";}
  }
  else {
    for (int i = 0; i <= numberOfSpaces; i++) {
      message = message + " ";
    }
  }

  lcd.print(message);
  if (lastDisplayedOnScreen == 6) {lastDisplayedOnScreen = 0;}
  else {lastDisplayedOnScreen = lastDisplayedOnScreen + 1;}
  }
}

//create a couple timers that will fire repeatedly every x ms
TimedAction updateScreenThread = TimedAction(3000, updateScreen);

void initialLCDConfig(){
  lcd.begin(16, 2);
  // Print a message to the LCD.
  lcd.print("---SOLARBERRY---");
  lcd.setCursor(0, 1);
  lcd.print("Waiting4Connect");
  lcd.blink();
 }

void setup() {
  // Setup LCD and print initial waiting message
  initialLCDConfig();

  // Set all of the RGB LEDs as output and set it as it's initial colour
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);  
  setColour(255, 0, 100);  // red

  pinMode(relayPin, OUTPUT);
  
  Serial.begin(9600); // start serial port at 9600 bps
  
  oneWireSensors.begin();

   // Initialize the INA219.
  // By default the initialization will use the largest range (32V, 2A).  However
  // you can call a setCalibration function to change this range (see comments).
  ina219_in.begin();
  ina219_out.begin();
  ina219_batt.begin();
  // To use a slightly lower 32V, 1A range (higher precision on amps):
//  ina219_in.setCalibration_solarberry();
//  ina219_out.setCalibration_solarberry();
//  ina219_batt.setCalibration_solarberry();
  ina219_in.setCalibration_32V_1A();
  ina219_out.setCalibration_32V_1A();
  ina219_batt.setCalibration_32V_1A();
  // Or to use a lower 16V, 400mA range (higher precision on volts and amps):
  //ina219.setCalibration_16V_400mA();
  
  establishContact();  // send a byte to establish contact until receiver responds

  battery_percent = 100; // TODO - Instead of starting this off at zero, pull a recent value from the db
  total_battery_Ah = 10000;
  battery_Ah = 10000;
}



void loop() {
  updateScreenThread.check();
  // if we get a valid byte, read analog ins:
  while (Serial.available() > 0) {
    // get incoming byte:
    in = Serial.readStringUntil('\n');
    if(in.startsWith("init")){
      readytoroll = true;
      setColour(0, 255, 255);  // update the RGB LED to aqua
    }
    else if ((in == "current_in")&&(readytoroll)) {
      float current_mA = ina219_in.getCurrent_mA()/1000;
      String valueString = String(current_mA);
      Serial.println(in + ":" + valueString);
      metrics[CURRENT_IN] = valueString;
    }
    else if ((in == "temperature_c")&&(readytoroll)) {
      oneWireSensors.requestTemperatures(); // Send the command to get temperatures
      float temperature_c = oneWireSensors.getTempCByIndex(0);
      String valueString = String(temperature_c);
      Serial.println(in + ":" + valueString);
      metrics[TEMPERATURE_C] = valueString;
    }
    else if ((in == "current_battery")&&(readytoroll)) {
      float current_mA = ina219_batt.getCurrent_mA();
      String valueString = String(current_mA);
      Serial.println(in + ":" + valueString);
      metrics[CURRENT_BATTERY] = valueString;
    }
    else if ((in == "current_out")&&(readytoroll)) {
      float current_mA = ina219_out.getCurrent_mA()/1000;
      String valueString = String(current_mA);
      Serial.println(in + ":" + valueString);
      metrics[CURRENT_OUT] = valueString;
    }
    else if ((in == "voltage_in")&&(readytoroll)) {
      float busvoltage = ina219_in.getBusVoltage_V();
      String valueString = String(busvoltage);
      Serial.println(in + ":" + valueString);
      metrics[VOLTAGE_IN] = valueString;
    }
    else if ((in == "voltage_battery")&&(readytoroll)) {
      float busvoltage = ina219_batt.getBusVoltage_V();
      String valueString = String(busvoltage);
      Serial.println(in + ":" + valueString);
      metrics[VOLTAGE_BATTERY] = valueString;
    }
    else if ((in.startsWith("battery_percent"))&&(readytoroll)) {
      
//      // Get current in
//      float current_in = ina219_in.getCurrent_mA();
//
//      // Get current out
//      float current_out = ina219_out.getCurrent_mA();
//      
//      // Work out what they are as Ah, divide it by the frequency of polling
//      int Ah_divisor = 3600/battery_percent_query_frequency;
//
//      float Ah_in = current_in/Ah_divisor;
//      float Ah_out = current_out/Ah_divisor;
//
////       Serial.println(Ah_in);
////       Serial.println(Ah_out);
//
//      battery_Ah = battery_Ah + Ah_in - Ah_out;
//
////      Serial.println(battery_Ah);
////
////      Serial.println("total"+String(total_battery_Ah));
////      Serial.println("battery"+String(battery_Ah));
////      Serial.println(float(100)/float(total_battery_Ah));
//      float battery_percent = (float(100) / float(total_battery_Ah)) * battery_Ah;
//      
////      Serial.println("batterypct"+String(battery_percent));
//
//      float value = battery_percent;
//
//      String valueString = String(value);
//      Serial.println(in + ":" + valueString);
      String pct = getValue(in,'_',2);
      metrics[BATTERY_PERCENT] = pct;
      Serial.println("battery_percent:" + pct);
//
//      
    }
    else if ((in == "voltage_out")&&(readytoroll)) {
      float busvoltage = ina219_out.getBusVoltage_V();
      String valueString = String(busvoltage);
      Serial.println(in + ":" + valueString);
      metrics[VOLTAGE_OUT] = valueString;
    }
    else if ((in == "poweron")&&(readytoroll)){
        controlPower(1);
    }
    else if ((in == "poweroff")&&(readytoroll)){
        controlPower(0);
    }
    else if ((in == "calibrate")){
        metrics[BATTERY_PERCENT] = String(100);
    }
//    else {
//      Serial.println("unrecognised or uninitialised");
//    }
  }
}

void controlPower(bool on){
  if (on == true){
    digitalWrite(relayPin, 1);
    setColour(0,255,255);
  }
  else{
    digitalWrite(relayPin, 0);
    setColour(255,0,0);
  }
}

//void updateMetric(String in, float value){
//      String valueString = String(value);
//      Serial.println(in + ":" + valueString);
//      metrics[CURRENT_BATTERY] = valueString;
//}

void establishContact() {
  while (Serial.available() <= 0) {
    delay(300);
    Serial.println("ready");
  }
}

void setColour(int red, int green, int blue)
{
  analogWrite(redPin, red);
  analogWrite(greenPin, green);
  analogWrite(bluePin, blue);  
}

// http://stackoverflow.com/questions/9072320/split-string-into-string-array
String getValue(String data, char separator, int index)
{
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length()-1;

  for(int i=0; i<=maxIndex && found<=index; i++){
    if(data.charAt(i)==separator || i==maxIndex){
        found++;
        strIndex[0] = strIndex[1]+1;
        strIndex[1] = (i == maxIndex) ? i+1 : i;
    }
  }

  return found>index ? data.substring(strIndex[0], strIndex[1]) : "";
}
