import machine
from machine import Pin, SoftI2C, PWM, RTC
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
from time import sleep

I2C_ADDR = 0x27
totalRows = 2
totalColumns = 16

i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=10000)     #initializing the I2C method for ESP32

lcd = I2cLcd(i2c, I2C_ADDR, totalRows, totalColumns)

# keypad hw-136 pins
SCL_PIN = 32
SDO_PIN = 35
NUM_KEYS = 16

# buzzer param
BUZZER_PIN = 25
NOTES_FREQ = [261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 
              369.99, 392, 415.30, 440, 466.16, 493.88]
BUZZER_NOTES = [0, 5, 0, 5]
BUZZER_REPEAT = 5
BUZZER_DELAY = 1

clock_pin = Pin(SCL_PIN, Pin.OUT)
key_pin = Pin(SDO_PIN, Pin.IN)
buzzer_pin = Pin(BUZZER_PIN, Pin.OUT)

rtc = RTC()
curr_year, curr_month, curr_day, curr_dayweek, curr_hour, curr_min, curr_sec, curr_ms = rtc.datetime()
alarm_hour = 5; alarm_min = 0; alarm_sec = 0

# page index and updates
page_idx = 0 # 0: main page, 1: alarm page
page_upd = 0 # to force update the display

# time pos and border
cur_pos = 7
LEFT_BORDER = 7
RIGHT_BORDER = 14
"""
    ALARM UI
    Alarm: hh:mm:ss
    
    7: h1, 8:h0
    10: m1, 11:m0
    13: s1, 14:s0

    ---------------

    MAIN UI
    Time: hh:mm:ss
    Date: DD:MM:YYYY

    6: h1, 7:h0
    9: m1, 10:m0
    12: s1, 13:s0

    
"""

# menu control
KEY_ALARM = 10
KEY_BACK = 12
KEY_UP = 14
KEY_DOWN = 15
KEY_LEFT = 13
KEY_RIGHT = 16

def readKeypad():
    key = -1
    for i in range(NUM_KEYS):
        clock_pin.off()
        if (key_pin.value() == 0):
            key = i+1
        clock_pin.on()
    return key


def checkBuzzer():
    # buzzer = PWM(buzzer_pin)
    # if ((alarm_hour == curr_hour) and (alarm_min == curr_min) and (alarm_sec == curr_sec)):
    #     buzzer.duty(50)
    #     # for n in range(BUZZER_REPEAT):
    #     #     for note in BUZZER_NOTES:
    #     #         buzzer.freq(NOTES_FREQ[note])
    #     sleep(BUZZER_DELAY)
    # buzzer.duty(0)

    # buzzer.deinit()
    
    return

def updateTime():
    global curr_year, curr_month, curr_day, curr_dayweek, curr_hour, curr_min, curr_sec, curr_ms

    rtc = RTC()
    curr_year, curr_month, curr_day, curr_dayweek, curr_hour, curr_min, curr_sec, curr_ms = rtc.datetime()
    c_Y3 = curr_year//1000; c_Y2 = curr_year//100; c_y1 = curr_year//10; c_y0 = curr_year%10
    c_M1 = curr_month//10; c_M0 = curr_month%10
    c_D1 = curr_day//10; c_D0 = curr_day%10

    c_m1 = curr_hour//10; c_m0 = curr_hour%10
    c_m1 = curr_month//10; c_m0 = curr_month%10
    c_m1 = curr_month//10; c_m0 = curr_month%10

    # update only when changed


    rtc = RTC()
    curr_year, curr_month, curr_day, curr_dayweek, curr_hour, curr_min, curr_sec, curr_ms = rtc.datetime()

    return

def mainPage(pressed):
    global page_idx
    page_idx = 0

    lcd.clear()
    lcd.blink_cursor_off()

    lcd.move_to(0, 0)
    lcd.putstr(f"Time: {curr_hour:02}:{curr_min:02}:{curr_sec:02}")
    lcd.move_to(0, 1)
    lcd.putstr(f"Date: {curr_day:02}-{curr_month:02}-{curr_year:04}")

    if (pressed == 13):
        page_idx = 1
    return

def manualValue(pos, key):
    global alarm_hour, alarm_min, alarm_sec
    if (pos == 7):
        if (key < 3):
            alarm_hour = alarm_hour%10 + 10*key

    elif (pos == 8):
        if (alarm_hour//10 == 1 or (alarm_hour//10 == 2 and key < 4)):
            alarm_hour = 10*(alarm_hour//10) + key

    elif (pos == 10):
        if (key < 6):
            alarm_min = alarm_min%10 + 10*key

    elif (pos == 11):
        alarm_min = 10*(alarm_min//10) + key

    elif (pos == 13):
        if (key < 6):
            alarm_sec = alarm_sec%10 + 10*key

    elif (pos == 14):
        alarm_sec = 10*(alarm_sec//10) + key

    return

def changeValue(pos, mode):
    global alarm_hour, alarm_min, alarm_sec

    if (pos == 7):
        if (mode == 0):
            if (alarm_hour+10 < 24):
                alarm_hour += 10
        else:
            if (alarm_hour-10 >= 0):
                alarm_hour -= 10
            
    elif (pos == 8):
        if (mode == 0):
            if (alarm_hour+1 < 24):
                alarm_hour += 1
        else:
            if (alarm_hour-1 >= 0):
                alarm_hour -= 1

    elif (pos == 10):
        if (mode == 0):
            if (alarm_min+10 < 60):
                alarm_min += 10
        else:
            if (alarm_min-10 >= 0):
                alarm_min -= 10

    elif (pos == 11):
        if (mode == 0):
            if (alarm_min+1 < 60):
                alarm_min += 1
        else:
            if (alarm_min-1 >= 0):
                alarm_min -= 1

    elif (pos == 13):
        if (mode == 0):
            if (alarm_sec+10 < 60):
                alarm_sec += 10
        else:
            if (alarm_sec-10 >= 0):
                alarm_sec -= 10

    elif (pos == 14):
        if (mode == 0):
            if (alarm_sec+1 < 60):
                alarm_sec += 1
        else:
            if (alarm_sec-1 >= 0):
                alarm_sec -= 1
    
    return

def updateAlarmPage():
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr(f"Alarm: {alarm_hour:02}:{alarm_min:02}:{alarm_sec:02}")
    lcd.move_to(0, 1)
    lcd.putstr("< | ^ | V  | > ")
    lcd.move_to(cur_pos, 0)
    lcd.blink_cursor_on()

    return

def alarmPage(pressed):
    global page_idx, cur_pos, page_upd
    page_idx = 1

    if (pressed == KEY_BACK):
        page_idx = 0
        
    elif (pressed < 10):
        manualValue(cur_pos, pressed)

    elif (pressed == KEY_UP):
        changeValue(cur_pos, 0)

    elif (pressed == KEY_DOWN):
        changeValue(cur_pos, 1)

    elif (pressed == KEY_LEFT):
        if (cur_pos > LEFT_BORDER):
            if (cur_pos == RIGHT_BORDER-1) or (cur_pos == RIGHT_BORDER-4):
                cur_pos -= 2
            else:
                cur_pos -= 1
        lcd.move_to(cur_pos, 0)

    elif (pressed == KEY_RIGHT):
        if (cur_pos < RIGHT_BORDER):
            if (cur_pos == LEFT_BORDER+1) or (cur_pos == LEFT_BORDER+4):
                cur_pos += 2
            else:
                cur_pos += 1
        lcd.move_to(cur_pos, 0)

    updateAlarmPage()

    return

def pageControl():
    global page_idx, cur_pos

    key = readKeypad()
    
    if (key != -1):
        if (page_idx == 0):
            mainPage(key)
        elif (page_idx == 1):
            alarmPage(key)

while True:
    pageControl()
    checkBuzzer()
    updateTime()
