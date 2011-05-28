SEND_SMS = True
DISCOUNT = True
DISCOUNT_PERCENT = 10
COUNT_FOR_DISCOUNT = 2

EMS = 300
COURIER = 300

try:
    from local_settings import *
except ImportError:
    pass