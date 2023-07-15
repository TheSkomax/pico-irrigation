from machine import Pin, ADC
from time import sleep
import ds1302


ds = ds1302.DS1302(Pin(18), Pin(17), Pin(16))
#ds.date_time([2023, 6, 18, 6, 18, 50, 20])
#
minute_switch = ADC(26)
mode_switch = ADC(27)
day_switch = ADC(28)
#rtc = machine.RTC()

led = Pin(25, Pin.OUT)
led(0)

relay = Pin(19, Pin.OUT)
relay.value(0)
sleep(1)

morning_target_time = "6:0:0"
evening_target_time = "20:0:0"

def get_minute_switch_pos():
    value = round(minute_switch.read_u16() * 3.3 / 65536, 2)
    
    if value < 0.4:
        minute = 5
    elif value >= 0.4 and value < 0.8:
        minute = 10
    elif value >= 0.8 and value < 1.2:
        minute = 15
    elif value >= 1.2 and value < 1.6:
        minute = 20
    elif value >= 1.6 and value < 2.0:
        minute = 25
    elif value >= 2.0 and value < 2.4:
        minute = 30
    elif value >= 2.4 and value < 2.8:
        minute = 35
    elif value >= 2.8 and value < 3.0:
        minute = 40
    elif value > 3.0:
        minute = 60
    return minute

def get_mode_switch_pos():
    value = round(mode_switch.read_u16() * 3.3 / 65536, 2)

    if value >= 0 and value < 1:
        mode = "morning"
    elif value >= 1.6 and value < 2.99:
        mode = "evening"
    elif value > 3:
        mode = "both"
    return mode
    
def get_day_switch_pos():
    value = round(day_switch.read_u16() * 3.3 / 65536, 2)
    
    if value >= 0 and value < 1:
        day = "everyday"
    elif value >= 1.6 and value < 3:
        day = "other"
    elif value > 3:
        day = "third"
    return day
    

def write_log(message):
    f = open("log.txt", "a")
    f.write(f"{date_now()} {time_now_hms()} {message}\n")
    # f.writelines(f"{date_now()} {time_now_hms()} with settings: {get_minute_switch_pos()}min {get_mode_switch_pos()} {get_day_switch_pos()}\n")
    f.close()


def date_now():
    (Y,M,D,day,hr,m,s) = ds.date_time()
    date_today = f"{D}.{M}.{Y}"
    return date_today


def time_now_hms():
    (Y,M,D,day,hr,m,s) = ds.date_time()
    time_now_hms = f"{hr}:{m}:{s}"
    return time_now_hms


def relay_open():
    relay(0)
    write_log("Relay opened!")


def relay_close():
    relay.value(1)
    write_log("Relay closed!")
    
    
def start_irrigation(minutes):
    print("Starting irrigation!")
    write_log("Starting irrigation process")
    write_log("Starting pump - closing relay")
    relay_close()
    led(1)

    write_log(f"Sleeping for {minutes} minutes")
    sleep(minutes * 60)

    write_log("Stopping pump - opening relay")
    relay_open()
    led(0)
    write_log("Irrigation process complete")
    print("Irrigation done!\n")


def main():
    print("Running\n")

    while True:       
        minute_switch_value = get_minute_switch_pos()
        mode_switch_value = get_mode_switch_pos()
        day_switch_value = get_day_switch_pos()
        
        #evening_target_time = "20:15:0"
        conditions = (time_now_hms() == morning_target_time and mode_switch_value != "evening",
                      time_now_hms() == evening_target_time and mode_switch_value != "morning")
        
        print(conditions)
        print(minute_switch_value, "mins", mode_switch_value, day_switch_value)
        print(time_now_hms(), "\n")
        
        if True in conditions:
            start_irrigation(minute_switch_value)

        sleep(1)

#
if __name__ == "__main__":
    main()

