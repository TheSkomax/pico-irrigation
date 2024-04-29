from machine import Pin, ADC
from time import sleep
import uos


minute_switch = ADC(26)
mode_switch = ADC(27)
day_switch = ADC(28)

led = Pin(25, Pin.OUT)
led(0)

lightsen = Pin(16, Pin.IN, Pin.PULL_UP)

relay = Pin(17, Pin.OUT)
relay.value(0)
sleep(1)


def get_minute_switch_pos():
    value = round(minute_switch.read_u16() * 3.3 / 65536, 2)
    
    if value < 0.4:
        minute = 5
    elif value >= 0.4 and value < 0.8:
        minute = 2
    elif value >= 0.8 and value < 1.2:
        minute = 4
    elif value >= 1.2 and value < 1.6:
        minute = 6
    elif value >= 1.6 and value < 2.0:
        minute = 8
    elif value >= 2.0 and value < 2.4:
        minute = 10
    elif value >= 2.4 and value < 2.8:
        minute = 15
    elif value >= 2.8 and value < 3.0:
        minute = 20
    elif value > 3.0:
        minute = 25
    return minute

def get_mode_switch_pos():
    value = round(mode_switch.read_u16() * 3.3 / 65536, 2)

    if value >= 0 and value < 1.59:
        mode = "morning"
    elif value >= 1.6 and value < 2.99:
        mode = "evening"
    elif value > 3:
        mode = "both"
    else:
        print("!!", value)
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
    f = open("uptime.txt", "r")
    uptime = f.read()
    f.close()
    
    f = open("log.txt", "a")
    f.write(f"{uptime}  {message}\n")
    # f.writelines(f"settings: {get_minute_switch_pos()}min {get_mode_switch_pos()} {get_day_switch_pos()}\n")
    f.close()


def write_uptime():
    write_log("Updating uptime")
    f = open("uptime.txt", "r")
    uptime = int(f.read())
    new_uptime = str(uptime + 1)
    f.close()

    f = open("uptime.txt", "w")
    f.write(new_uptime)
    f.close()


def reset_uptime():
    f = open("uptime.txt", "w")
    f.write("0")
    f.close()
    write_log("Uptime reset")
    

def check_file_size():
    info = uos.stat("log.txt")
    size = int(info[6])
        
    if (size / 1000) > 50000:
        f = open("log.txt", "w")
        f.close()
        write_log("Log was cleared due to file size")
        

def relay_open():
    relay(0)
    write_log("Relay opened!")


def relay_close():
    relay.value(1)
    write_log("Relay closed!")
    
    
def start_irrigation(minutes):
    #print("Starting irrigation!")
    write_log("Starting irrigation process")
    write_log("Starting pump - closing relay")
    relay_close()

    write_log(f"Sleeping for {minutes} minutes")
    sleep(int(minutes) * 60)

    write_log("Stopping pump - opening relay")
    relay_open()

    write_log("Irrigation process complete")
    #print("Irrigation done!\n")


def sleep_for_hours(hours):
    sleep_time = hours * 60 * 60
    write_log(f"Going to sleep for {hours} hours")
    sleep(sleep_time)
    
    
def light_continuity():
    write_log("Checking light continuity for 10 seconds")
    repeat = 0
    values = []
    
    while repeat != 10:
        #print("dark =", lightsen.value())
        values.append(lightsen.value())
        repeat = repeat + 1
        sleep(1)
    
    all_same = all(x == values[0] for x in values)
    #print(all_same, values)
    
    if all_same and True in values:
        write_log("EVENING (all dark)")
        return True, "evening"
    if all_same and False in values:
        write_log("MORNING (all light)")
        return True, "morning"
    else:
        write_log("Continuity NOT confirmed")
        return False, None


def mainold():
    print("Running\n")

    while True:       
        minute_switch_value = get_minute_switch_pos()
        mode_switch_value = get_mode_switch_pos()
        day_switch_value = get_day_switch_pos()
        
        #evening_target_time = "20:15:0"
        #conditions = (time_now_hms() == morning_target_time and mode_switch_value != "evening",
        #              time_now_hms() == evening_target_time and mode_switch_value != "morning")
        
        print(conditions)
        print(minute_switch_value, "mins", mode_switch_value, day_switch_value)
        
        if True in conditions:
            start_irrigation(minute_switch_value)

        sleep(1)
        
def led_flash():
    x = 0
    while x != 3:
        led(1)
        sleep(0.5)
        led(0)
        sleep(0.5)
        x = x+1
    led(1)


def debug_only():
    while True:
        minutes = get_minute_switch_pos()
        mode = get_mode_switch_pos()
        day = get_day_switch_pos()
        
        print(minutes, mode, day)
        sleep(2)





def main():
    light_list = []
    write_log("=====\n\n========================================================================================\nSTARTED")
    
    reset_uptime()
    led_flash()
    
    while True:
        write_log("-----\n\n--- CHECKING ---")
        lightsensor_value = lightsen.value()
        write_log(f"lightsensor_value ={lightsensor_value}")
        
        check_file_size()
        write_log("check_file_size DONE")
        
        if lightsensor_value not in light_list and len(light_list) > 0:
            write_log("Detected different value of the lightsensor_value")
            continuity_confirmed, time_of_day = light_continuity()
            
            if continuity_confirmed:
                write_log("Continuity confirmed - clearing light_list")
                light_list = []
                light_list.append(lightsensor_value)
                
                write_log("Getting values from switches")
                minutes = get_minute_switch_pos()
                mode = get_mode_switch_pos()
                day = get_day_switch_pos()
                
                write_log(f"Check:          MINUTES = {minutes}")
                write_log(f"Check:          MODE    = {mode}")
                write_log(f"Check:          DAY     = {day}")
                
                if mode == time_of_day:
                    write_log(f"IRRIGATION - mode: {mode}, status: {time_of_day}")
                    start_irrigation(minutes)
                                       
                elif mode == "both" and time_of_day is not None:
                    write_log(f"IRRIGATION - mode: {mode}, status: {time_of_day}")
                    start_irrigation(minutes)
                    
                else:
                    write_log(f"NO IRRIGATION !!! - mode: {mode}, status: {time_of_day}")
                
        else:
            light_list.append(lightsensor_value)
            write_log(f"lightsensor_value added to light_list = {lightsensor_value}")
            
        write_log(f"light_list: {light_list} - {len(light_list)} checks")
        write_log("SLEEPING for 1 hour -------------------------------------------------")
        sleep(3600)
        write_uptime()

if __name__ == "__main__":
    # print("* STARTED *")
    main()
    #debug_only()





#while True:
#    print(lightsen.value())
#    sleep(1)
#led_flash()
#light_continuity()
#debug_only()

