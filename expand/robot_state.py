import time

def awake():
    return 6 <= time.localtime().tm_hour < 22