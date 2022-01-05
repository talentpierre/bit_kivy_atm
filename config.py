import credentials

## mediafiles
VIDEO_PATH = 'media/Sample.mp4'
CLICK_SOUND_PATH = 'media/click1.mp3'

## nv9usb+
BILLER_INTERFACE_PATH = '/dev/ttyACM0'

## programm constants
WAITING_TIME = 60

## paymentprovider
# --> 'lntxbot', 'lnbits'
PAYMENT_PROVIDER = 'lnbits'

## priceprovider
# --> 'opennode'
PRICE_PROVIDER = 'opennode'

## credentials
# lnbits
LNBITS_ADMIN_KEY = credentials.LNBITS_ADMIN_KEY
LNBITS_INVOICE_KEY = credentials.LNBITS_INVOICE_KEY
LNBITS_URL = credentials.LNBITS_URL

# lntxbot
LNTXBOT_ADMIN_KEY = credentials.LNTXBOT_ADMIN_KEY
LNTXBOT_URL = credentials.LNTXBOT_URL

######################################

## lnbits helper
withdraw_id = ''

## lntxbot helper
start_balance = 0
