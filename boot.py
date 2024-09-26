from machine import RTC
import network
import ntptime
import time

station = network.WLAN(network.STA_IF)

print("Connecting to server...")
def connect(id, pswd):
  ssid = id
  password = pswd
  if station.isconnected() == True:
    print("Already connected")
    return
  station.active(True)
  station.connect(ssid, password)
  while station.isconnected() == False:
    pass
  print("Connection successful")
  print(station.ifconfig())
 
def disconnect():
  if station.active() == True: 
   station.active(False)
  if station.isconnected() == False:
    print("Disconnected") 

connect("Iprons", "Nurhakim!nt3rnet")


print("\nSetting RTC to current time...")
rtc = RTC()
ntptime.settime()
(year, month, day, weekday, hours, minutes, seconds, subseconds) = rtc.datetime()
print ("UTC Time: ")
print((year, month, day, hours, minutes, seconds))

sec = ntptime.time()
timezone_hour = 7.00
timezone_sec = timezone_hour * 3600
sec = int(sec + timezone_sec)
(year, month, day, hours, minutes, seconds, weekday, yearday) = time.localtime(sec)
print ("WIB Time: ")
print((year, month, day, hours, minutes, seconds))
rtc.datetime((year, month, day, 0, hours, minutes, seconds, 0))
disconnect()
print("RTC has been set to current time!\n")
