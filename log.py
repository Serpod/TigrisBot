import datetime
def log_info(msg):
    date = datetime.datetime.now()
    print("{} >>> {}".format(date, msg))

def log_error(msg):
    date = datetime.datetime.now()
    print("{} *** {}".format(date, msg))
