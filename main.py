import os
os.environ['KIVY_VIDEO'] = 'ffpyplayer'
os.environ['KIVY_AUDIO'] = 'ffpyplayer'

import logging
import pyautogui
import pyautogui as pyautogui
import qrcode
import requests
import time

from datetime import datetime
from functools import partial

import kivy
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix import video
from kivy.uix.video import Video

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout

from credentials import API_ADMIN_KEY, API_INVOICE_KEY, API_URL
from nv9biller import Biller

#Window.size = (1920, 1080)
#Window.fullscreen = True
#Window.borderless = '0'
Window.top = int((pyautogui.size().height - Window.height)) / 2
Window.left = int((pyautogui.size().width - Window.width)) / 2


class VideoBoxLayout(MDBoxLayout):
    '''A layout for the video screen.'''
    button_color = ObjectProperty(None)
    video_state = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(VideoBoxLayout, self).__init__(**kwargs)
        self.button_color = 1, 0, 0, 0
        self.action = time.time()
        Logger.debug(f"VideoBoxLayout: instance of VideoBoxLayout initalized - {datetime.now()}")

    def screensaver(self, _):
        '''It checks if the screensaver should be active.'''
        Logger.debug(f"VideoBoxLayout: screensaver check - {datetime.now()}")
        if time.time() > self.action + 30:
            MDApp.get_running_app().root.ids.scrmanager.current = 'blackscreen'
            self.start_timer_event.cancel()
            Logger.info(f"VideoBoxLayout: screensaver videobox on - {datetime.now()}")

    def start_timer(self):
        '''A timer which calls the screensaver method every second.'''
        self.start_timer_event = Clock.schedule_interval(self.screensaver, 1)
        self.action = time.time()
        Logger.debug(f"VideoBoxLayout: start_timer called - {datetime.now()}")

    def stop_timer(self):
        '''A function that cancels the start_timer because it's not necessary anymore.'''
        self.start_timer_event.cancel()
        self.action = time.time()
        Logger.debug(f"VideoBoxLayout: stop_timer called - {datetime.now()}")


class InfoBoxLayout(MDBoxLayout):
    '''A layout for the information screen.'''

    def __init__(self, **kwargs):
        super(InfoBoxLayout, self).__init__()
        self.action = time.time()

        self.info_text = f"Beachten Sie, dass es sich hierbei um einen LightningATM handelt.\n" \
            f"Stellen Sie sicher, dass Sie ausreichend Inbound Capacity besitzen " \
            f"oder Inflight Channels in Ihrem Wallet supported werden. \n" \
            f"Aktuell kann kein Bargeld ausgezahlt werden, sollte die Zahlung fehlschlagen."

        self.title = 'Achtung'
        Logger.debug(f"InfoBoxLayout: instance of InfoBoxLayout initialized - {datetime.now()}")

    def screensaver(self, _):
        '''It checks if the screensaver should be active.'''
        Logger.debug(f"InfoBoxLayout: screensaver check - {datetime.now()}")
        if time.time() > self.action + 30:
            MDApp.get_running_app().root.ids.scrmanager.current = 'blackscreen'
            self.start_timer_event.cancel()
            Logger.info(f"InfoBoxLayout: screensaver videobox on - {datetime.now()}")

    def start_timer(self):
        '''A timer which calls the screensaver method every second.'''
        self.start_timer_event = Clock.schedule_interval(self.screensaver, 1)
        self.action = time.time()
        Logger.debug(f"InfoBoxLayout: start_timer called - {datetime.now()}")

    def stop_timer(self):
        '''A function that cancels the start_timer because it's not necessary anymore.'''
        self.start_timer_event.cancel()
        self.action = time.time()
        Logger.debug(f"InfoBoxLayout: stop_timer called - {datetime.now()}")


class PaymentBoxLayout(MDBoxLayout):
    '''A layout for the information screen.'''
    price = StringProperty()
    inserted_value = StringProperty()
    information_label = StringProperty()
    image_path = StringProperty('')

    def __init__(self, **kwargs):
        super(PaymentBoxLayout, self).__init__()

        self.was_withdraw_used = False
        self.information_label = 'Bitte Bargeld \n einzahlen. '

        self.fiat = 0
        self.fee = 1.02
        self.btcprice = 0
        self.satprice = 0
        self.price = ''
        self.inserted_value = f"{self.fiat:.2f} Euro"

        self.set_prices()

        self.biller = Biller('/dev/ttyACM0')

    def set_prices(self):
        '''It gets the bitcoin price and sets the price variables.'''
        self.btcprice = float(requests.get('https://api.opennode.co/v1/rates').json()['data']['BTCEUR']['EUR'])
        self.satprice = self.btcprice / 100_000_000
        self.price = f"{round(self.satprice * self.fee * 10_000, 2):.2f} Cent/100Sats \n{round(self.btcprice * self.fee, 2):.2f} Euro/bitcoin"

#    def test_fiat_change(self, _):
#        '''A test method for simulating fiat input.'''
#        self.fiat = 2.00

    def update_fiat_input(self, _):
        '''The method is called by a timer to update the fiat input by the user.'''
        events = self.biller.poll()
        for event in events:
            print(str(event))
            if('Credit -> 5.00' in str(event)):
                print('5 Euro')
                self.fiat += 5
            if('Credit ->10.00' in str(event)):
                print('10 Euro')
                self.fiat += 10
            if('Credit -> 20.00' in str(event)):
                print('20 Euro')
                self.fiat += 20
            if('Credit -> 50.00' in str(event)):
                print('50 Euro')
                self.fiat += 50

    def update_price(self, _):
        '''The method is called by a timer to setup the price.'''
        self.set_prices()

    def update_inserted_value(self, _):
        '''The method is called by a timer to update the inserted_value label.'''
        self.inserted_value = f"{self.fiat:.2f} Euro"

    def start_clock(self):
        '''The method starts several update timer.'''
        self.price_event = Clock.schedule_interval(self.update_price, 60)
        self.inserted_value_event = Clock.schedule_interval(self.update_inserted_value, 1)
        self.fiat_input_event = Clock.schedule_interval(self.update_fiat_input, 1)
        self.setup_cash_acceptor()
        self.image_path = ''

#        for testing if cash acceptor is not available
#        self.test_fiat_change_event = Clock.schedule_once(self.test_fiat_change, 15)

    def stop_clock(self):
        '''The method stops several update timer.'''
        self.price_event.cancel()
        self.inserted_value_event.cancel()
        self.fiat_input_event.cancel()
        self.disable_cash_acceptor()

    def start_payment_process(self):
        '''The method initiates the payment process and
        starts a timer which checks the payment status.
        '''
        if self.fiat:
            fiat = self.fiat
            self.fiat = 0
            amount = int(round(fiat / self.satprice))
            title = 'bit_lightning_atm'
            withdraw_information = self.get_new_payreq_information(amount, title)
            lnurl = withdraw_information['lnurl']
            withdraw_id = withdraw_information['id']
            self.show_qr_code(lnurl)
            self.check_payment_event = Clock.schedule_interval(partial(self.withdraw_used, withdraw_id), 1)

    def get_new_payreq_information(self, amount, title):
        '''It requests a withdraw link and returns its details.'''
        url = f"{API_URL}/withdraw/api/v1/links"
        payload = {
            "title": title,
            "min_withdrawable": amount,
            "max_withdrawable": amount,
            "uses": 1,
            "wait_time": 1,
            "is_unique": True
        }
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": f"{API_ADMIN_KEY}"
        }
        response = requests.request("POST", url, json=payload, headers=headers).json()
        return response

    def withdraw_used(self, withdraw_id, _):
        '''The method is called by a timer and checks the payment status.'''
        url = f"{API_URL}/withdraw/api/v1/links/{withdraw_id}"
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": f"{API_INVOICE_KEY}"
        }
        response = requests.request("GET", url, headers=headers).json()
        was_used = response['used']
        if was_used:
            self.check_payment_event.cancel()
            self.stop_clock()
            MDApp.get_running_app().root.ids.image_id.opacity = 0
            self.information_label = 'Vielen Dank und \nbis bald.'
            Clock.schedule_once(self.payment_done, 10)

    def payment_done(self, _):
        '''The method is called after the payment was payed and switches back to the video screen.'''
        MDApp.get_running_app().root.ids.scrmanager.current = 'videoscreen'
        self.information_label = 'Bitte Bargeld \n einzahlen. '

    def show_qr_code(self, lnurl):
        '''The method presents the lnurl qr code on the payment screen.'''
        self.create_qrcode_img(lnurl)
        self.image_path = f"qrcodes/{lnurl[-10:]}.png"
        MDApp.get_running_app().root.ids.image_id.opacity = 1

    def create_qrcode_img(self, lnurl):
        '''The method creates a qr-code and stores the image in the current directory.'''
        qr = qrcode.QRCode()
        qr.add_data(lnurl.upper())
        img = qr.make_image(back_color=(0, 0, 0), fill_color=(255, 153, 0))
        img.save(f"qrcodes/{lnurl[-10:]}.png")


    def setup_cash_acceptor(self):
        '''The method initialises the parameters of the cash acceptor.'''
        print(f"{time.time()} - biller initialisation")
        print(f"SN: {self.biller.serial:08X}")

        self.biller.channels_set(self.biller.CH_ALL)
        self.biller.display_enable()
        self.biller.enable()

        print(f"{time.time()} - biller initialisation done")

    def disable_cash_acceptor(self):
        '''The method disables the cash acceptor and resets the parameters.'''
        print(f"{time.time()} - disabling biller")

        self.biller.disable()
        self.biller.display_disable()
        self.biller.channels_set(None)

        print(f"{time.time()} - disabling biller done")


class MyApp(MDApp):
    '''The main kivymd app.'''

    def build(self):
        '''The method builds the application based on the kivy file.'''
        return Builder.load_file("main.kv")


if __name__ == '__main__':
    MyApp().run()
