import machine, pyRTOS
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
SCL_PIN = 33
SDO_PIN = 32
NUM_KEYS = 16
SCL_PERIOD = 1 # in ms
key = -1
key_pin = Pin(SDO_PIN, Pin.IN)

# buzzer param
BUZZER_PIN = 25
NOTES_FREQ = [261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 
              369.99, 392, 415.30, 440, 466.16, 493.88]
BUZZER_NOTES = [0, 5, 0, 5]
BUZZER_REPEAT = 5
BUZZER_DELAY = 1500 # in ms

# RTC
rtc = RTC()
curr_year, curr_month, curr_day, x, curr_hour, curr_min, curr_sec, y = rtc.datetime()
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
KEY_ALARM = 11
KEY_BACK = 12
KEY_LEFT = 13
KEY_UP = 14
KEY_DOWN = 15
KEY_RIGHT = 16

def readKeypad(self):
    global key

    ### Setup code here
    clock_pin = Pin(SCL_PIN, Pin.OUT)
    clock_pin.on()
    print("Keypad ready!")
    ### End Setup code

    # Pass control back to RTOS
    yield

    # Main Task Loop
    while True:
        # print("Checking keys...")

        ### Work code here
        key = -1
        for i in range(NUM_KEYS):
            clock_pin.off()
            if (key_pin.value() == 0):
                key = i+1
            clock_pin.on()
        ### End Work code
        # if (key != -1):
        #     print(f"Pressed {key}")
        yield [pyRTOS.timeout(1)] # (Quick interval for fast checking)

def checkBuzzer(self):
    ### Setup code here
    buzzer_pin = Pin(BUZZER_PIN, Pin.OUT)
    print("Buzzer ready!")
    buzzer = PWM(buzzer_pin, duty=0)
    ### End Setup code

    # Pass control back to RTOS
    yield

    # Main Task Loop
    while True:
        # print("Checking buzzer...")

        ### Work code here
        if ((alarm_hour == curr_hour) and (alarm_min == curr_min) and (alarm_sec == curr_sec)):
            # buzzer_pin.on()
            buzzer.duty(50)
            for n in range(BUZZER_REPEAT):
                for note in BUZZER_NOTES:
                    buzzer.freq(round(NOTES_FREQ[note]))
                yield [pyRTOS.timeout(BUZZER_DELAY)]
        # buzzer_pin.off()
        buzzer.duty(0)
        ### End Work code
        yield [pyRTOS.timeout(100)] # (Check interval 100 ms)

def updateTime(self):
    global curr_year, curr_month, curr_day, x, curr_hour, curr_min, curr_sec, y
    global page_idx

    ### Setup code here
    rtc = RTC()
    print("Time updater ready!")
    ### End Setup code

    # Pass control back to RTOS
    yield

    # Main Task Loop
    while True:
        # print("Checking time updater...")

        ### Work code here
        curr_year, curr_month, curr_day, x, curr_hour, curr_min, curr_sec, y = rtc.datetime()
        yield [pyRTOS.timeout(100)]

        # update each time values on lcd (update manually to decrease lag)
        if (page_idx == 0):
            # update year
            pos_x = 12 
            str_year = f"{curr_year:04}"
            lcd.move_to(pos_x, 1)
            lcd.putstr(str_year)
            
            # update month
            pos_x = 9
            str_month = f"{curr_month:02}"
            lcd.move_to(pos_x, 1)
            lcd.putstr(str_month)

            # update day
            pos_x = 6
            str_day = f"{curr_day:02}"
            lcd.move_to(pos_x, 1)
            lcd.putstr(str_day)

            # update hour
            pos_x = 6
            str_hour = f"{curr_hour:02}"
            lcd.move_to(pos_x, 0)
            lcd.putstr(str_hour)

            # update minute
            pos_x = 9
            str_min = f"{curr_min:02}"
            lcd.move_to(pos_x, 0)
            lcd.putstr(str_min)

            # update second
            pos_x = 12
            str_sec = f"{curr_sec:02}"
            lcd.move_to(pos_x, 0)
            lcd.putstr(str_sec)
        ### End Work code

        yield [pyRTOS.timeout(100)] # (Update interval is 100 ms)

def setMainPage():
    lcd.clear()
    lcd.blink_cursor_off()
    lcd.hide_cursor()
    lcd.move_to(0, 0)
    lcd.putstr(f"Time: {curr_hour:02}:{curr_min:02}:{curr_sec:02}")
    lcd.move_to(0, 1)
    lcd.putstr(f"Date: {curr_day:02}-{curr_month:02}-{curr_year:04}")
    return

def setAlarmPage():
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr(f"Alarm: {alarm_hour:02}:{alarm_min:02}:{alarm_sec:02}")
    lcd.move_to(0, 1)
    lcd.putstr("< | ^ | V  | > ")
    lcd.move_to(cur_pos, 0)
    lcd.blink_cursor_on()
    return

def mainPage(pressed):
    global page_idx
    page_idx = 0

    if (pressed == KEY_ALARM):
        page_idx = 1
        setAlarmPage()
    return

def manualValue(pos, key):
    global alarm_hour, alarm_min, alarm_sec
    if (key == 10):
        num = 0
    else:
        num = key

    if (pos == 7):
        if (num < 3):
            alarm_hour = alarm_hour%10 + 10*num

    elif (pos == 8):
        alarm_hour = 10*(alarm_hour//10) + num

    elif (pos == 10):
        if (num < 6):
            alarm_min = alarm_min%10 + 10*num

    elif (pos == 11):
        alarm_min = 10*(alarm_min//10) + num

    elif (pos == 13):
        if (num < 6):
            alarm_sec = alarm_sec%10 + 10*num

    elif (pos == 14):
        alarm_sec = 10*(alarm_sec//10) + num

    lcd.move_to(7, 0)
    lcd.putstr(f"{alarm_hour:02}:{alarm_min:02}:{alarm_sec:02}")
    lcd.move_to(cur_pos, 0)

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

    lcd.move_to(7, 0)
    lcd.putstr(f"{alarm_hour:02}:{alarm_min:02}:{alarm_sec:02}")
    lcd.move_to(cur_pos, 0)

    return

def alarmPage(pressed):
    global page_idx, cur_pos, page_upd
    page_idx = 1

    if (pressed == KEY_BACK):
        page_idx = 0
        setMainPage()
        
    elif (0 <= pressed <= 10):
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

    return

def pageControl(self):
    global page_idx, key
    ### Setup code here
    page_idx = 0
    setMainPage()
    print("Page controller ready!")
    ### End Setup code

    # Pass control back to RTOS
    yield

    # Main Task Loop
    while True:
        # print("Checking controller...")

        ### Work code here
        if (page_idx == 0):
            mainPage(key)
        elif (page_idx == 1):
            alarmPage(key)
        ### End Work code

        yield [pyRTOS.timeout(200)] # (Update interval is 200 ms)

# Define the main function to handle the interrupt
def main():
    # Create tasks
    t1 = pyRTOS.Task(readKeypad, name="Read Keypad Task", priority=1)
    t2 = pyRTOS.Task(checkBuzzer, name="Check Buzzer Task", priority=1)
    t3 = pyRTOS.Task(updateTime, name="Update Time Task", priority=1)
    t4 = pyRTOS.Task(pageControl, name="Page Control Task", priority=1)

    # Add tasks to the RTOS
    pyRTOS.add_task(t1)
    pyRTOS.add_task(t2)
    pyRTOS.add_task(t3)
    pyRTOS.add_task(t4)

    # Start the RTOS
    print("Device started!")
    pyRTOS.start()

# Run the main function
main()