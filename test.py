import logging
import time
from datetime import datetime
from datetime import date


# ---------------- LOGGING ----------------
log_overview = logging.getLogger("overview")
log_overview.setLevel(logging.INFO)
log_formatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s",
                                  "%d.%m.%Y %H:%M:%S")
file_handler = logging.FileHandler("log_overview.log")
file_handler.setFormatter(log_formatter)
log_overview.addHandler(file_handler)

# log_days = logging.getLogger("days")
# log_days.setLevel(logging.INFO)
# log_formatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s",
#                                   "%d.%m.%Y %H:%M:%S")
# file_handler = logging.FileHandler("log_days.log")
# file_handler.setFormatter(log_formatter)
# log_days.addHandler(file_handler)


# placeholder values
relay_pin = 15
minutes = 15
time_morning = "6:00:00"
time_evening = "20:00:00"
day_setting = "everyday"
time_setting = "morning"


# placeholder time function
def time_now_hms():
    time_object = datetime.now()
    time_actual = time_object.strftime("%H:%M:%S")
    return time_actual


# placeholder date function
def date_now():
    date_object = date.today()
    date_actual = date_object.strftime("%d.%m.%Y")
    date_list = date_actual.split(".")
    list_int = [int(x) for x in date_list]
    list_str = [str(x) for x in list_int]
    date_actual = ".".join(list_str)
    return date_actual


def relay_open():
    # gpio.relay_pin(high)
    log_overview.warning("Relay opened!")


def relay_close():
    # gpio.relay_pin(low)
    log_overview.warning("Relay closed!")


def start_irrigation():
    log_overview.info("Starting irrigation process!")
    log_overview.info("Starting pump - closing relay")
    relay_close()

    log_overview.info(f"Sleeping for {minutes}")
    time.sleep(minutes)

    log_overview.info("Stopping pump - opening relay")
    relay_open()
    log_overview.info("Irrigation process complete")


def day_checker():
    if day_setting == "everyday":
        pass
    elif day_setting == "other":
        pass
    elif day_setting == "third":
        pass

    f = open("irrigation_days.txt", "a")
    f.writelines(f"{date_now()} {time_now_hms()} with settings: {minutes}min {time_setting} {day_setting}\n")
    f.close()

    # open and read the file after the appending:
    f = open("irrigation_days.txt", "r")
    lines = f.readlines()
    num_of_lines = len(lines)
    for line in lines:
        print(line)

    # f = open("irrigation_days.txt", "a")
    # f.write(f"\n{date_now()} {minutes}m {time_setting} {day_setting}")
    # f.close()

    if num_of_lines > 365:
        open('irrigation_days.txt', 'w').close()
        log_overview.warning("irrigation_days.txt cleared!!!")



def main():
    while True:
        conditions = (time_now_hms() == time_morning and (time_setting == "both" or time_setting == "morning"),
                      time_now_hms() == time_evening and (time_setting == "both" or time_setting == "evening"))

        if True in conditions:
            start_irrigation()


# if __name__ == "__main__":
#     main()

day_checker()