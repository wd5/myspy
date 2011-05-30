SEND_SMS = True

EMS = 300
COURIER = 300

try:
    from local_settings import *
except ImportError:
    pass