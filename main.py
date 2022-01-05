import os
os.environ['KIVY_VIDEO'] = 'ffpyplayer'
os.environ['KIVY_AUDIO'] = 'sdl2'

import importlib
import logging
import pyautogui
import pyautogui as pyautogui
import qrcode
import requests
import time

from datetime import datetime

import kivy
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix import video
from kivy.uix.video import Video

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from playsound import playsound

import config
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
        Logger.debug(f"VideoBoxLayout: start_timer - {datetime.now()}")

    def stop_timer(self):
        '''A method that cancels the start_timer because it's not necessary anymore.'''
        self.start_timer_event.cancel()
        self.action = time.time()
        Logger.debug(f"VideoBoxLayout: stop_timer - {datetime.now()}")


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
            Logger.info(f"InfoBoxLayout: screensaver infobox on - {datetime.now()}")

    def start_timer(self):
        '''A timer which calls the screensaver method every second.'''
        self.start_timer_event = Clock.schedule_interval(self.screensaver, 1)
        self.action = time.time()
        Logger.debug(f"InfoBoxLayout: start_timer - {datetime.now()}")

    def stop_timer(self):
        '''A function that cancels the start_timer because it's not necessary anymore.'''
        self.start_timer_event.cancel()
        self.action = time.time()
        Logger.debug(f"InfoBoxLayout: stop_timer - {datetime.now()}")

    def play_click_sound(self):
        '''The method plays a click sound.'''
        sound = SoundLoader.load(config.CLICK_SOUND_PATH)
        if sound:
            sound.play()


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
        self.start_time = 0
        self.payment_provider = importlib.import_module(f"paymentprovider.{config.PAYMENT_PROVIDER}", '.')
        self.price_provider = importlib.import_module(f"priceprovider.{config.PRICE_PROVIDER}", ".")

        Clock.schedule_once(self.update_price, 5)

        self.biller = Biller(config.BILLER_INTERFACE_PATH)
        Logger.debug(f"PaymentBoxLayout: instance of PaymentBoxLayout initialized - {datetime.now()}")

    def play_click_sound(self):
        '''The method plays a click sound.'''
        sound = SoundLoader.load(config.CLICK_SOUND_PATH)
        if sound:
            sound.play()

    def set_prices(self):
        '''It gets the bitcoin price and sets the price variables.'''
        try:
            self.btcprice = self.price_provider.get_btc_price()
        except Exception as e:
            MDApp.get_running_app().root.ids.scrmanager.current = 'supportscreen'
            Logger.critical(f"PaymentBoxLayout: set_prices - exchange rate error - {datetime.now()}")
            Logger.critical(f"{e}")
        else:
            self.satprice = self.btcprice / 100_000_000
            self.price = f"{round(self.satprice * self.fee * 10_000, 2):.2f} Cent/100Sats \n{round(self.btcprice * self.fee, 2):.2f} Euro/bitcoin"
            Logger.debug(f"PaymentBoxLayout: set_prices - {datetime.now()}")

#    def test_fiat_change(self, _):
#        '''A test method for simulating fiat input.'''
#        self.fiat = 2.00

    def update_fiat_input(self, _):
        '''The method is called by a timer to update the fiat input by the user.'''
        events = self.biller.poll()
        for event in events:
            Logger.debug(f"PaymentBoxLayout: update_fiat_input - event {str(event)} - {datetime.now()}")
            if 'Credit -> 5.00' in str(event):
                self.fiat += 5
                Logger.info(f"PaymentBoxLayout: update_fiat_input - fiat {self.fiat} - {datetime.now()}")
            if 'Credit ->10.00' in str(event):
                self.fiat += 10
                Logger.info(f"PaymentBoxLayout: update_fiat_input - fiat  {self.fiat} - {datetime.now()}")
            if 'Credit -> 20.00' in str(event):
                self.fiat += 20
                Logger.info(f"PaymentBoxLayout: update_fiat_input - fiat {self.fiat} - {datetime.now()}")
            if 'Credit -> 50.00' in str(event):
                self.fiat += 50
                Logger.info(f"PaymentBoxLayout: update_fiat_input - fiat {self.fiat} - {datetime.now()}")

    def update_price(self, _):
        '''The method is called by a timer to setup the price.'''
        self.set_prices()

    def update_inserted_value_label(self, _):
        '''The method is called by a timer to update the inserted_value label.'''
        self.inserted_value = f"{self.fiat:.2f} Euro"

    def start_clock(self):
        '''The method starts several update timer.'''
        self.price_event = Clock.schedule_interval(self.update_price, 60)
        self.inserted_value_event = Clock.schedule_interval(self.update_inserted_value_label, 1)
        self.fiat_input_event = Clock.schedule_interval(self.update_fiat_input, 1)
        self.setup_cash_acceptor()
        self.image_path = ''
        Logger.debug(f"PaymentBoxLayout: start_clock - {datetime.now()}")

#        for testing if cash acceptor is not available
#        self.test_fiat_change_event = Clock.schedule_once(self.test_fiat_change, 5)

    def stop_clock(self):
        '''The method stops several update timer.'''
        self.price_event.cancel()
        self.inserted_value_event.cancel()
        self.fiat_input_event.cancel()
        self.disable_cash_acceptor()
        Logger.debug(f"PaymentBoxLayout: stop_clock - {datetime.now()}")

    def start_payment_process(self):
        '''The method initiates the payment process and
        starts a timer which checks the payment status.
        '''
        Logger.debug(f"PaymentBoxLayout: start_payment_process - fiat {self.fiat} - {datetime.now()}")
        if self.fiat:
            Logger.info(f"PaymentBoxLayout: start_payment_process - withdraw initiated - fiat {self.fiat} - {datetime.now()}")
            fiat = self.fiat
            self.fiat = 0
            amount = int(round(fiat / self.satprice))
            Logger.info(f"PaymentBoxLayout: start_payment_process - withdraw initiated - sats {amount} - {datetime.now()}")
            try:
                lnurl = self.payment_provider.get_new_payreq_information(amount)
            except Exception as e:
                MDApp.get_running_app().root.ids.scrmanager.current = 'supportscreen'
                Logger.critical(f"PaymentBoxLayout: start_payment_process - payrequest error - {datetime.now()}")
                Logger.critical(f"{e}")
            else:
                self.show_qr_code(lnurl)
                self.check_payment_event = Clock.schedule_interval(self.withdraw_used, 1)
                self.start_time = time.time()

    def withdraw_used(self, _):
        '''The method is called by a timer and checks the payment status.'''
        try:
            was_used = self.payment_provider.get_payment_status()
        except Exception as e:
            self.check_payment_event.cancel()
            MDApp.get_running_app().root.ids.scrmanager.current = 'supportscreen'
            Logger.critical(f"PaymentBoxLayout: withdraw_used - payment status error - {datetime.now()}")
            Logger.critical(f"{e}")
        else:
            payment_time_is_too_long = time.time() > self.start_time + config.WAITING_TIME
            if was_used or payment_time_is_too_long:
                self.check_payment_event.cancel()
                self.stop_clock()
                MDApp.get_running_app().root.ids.image_id.opacity = 0
                if payment_time_is_too_long:
                    self.information_label = 'Payment \nfehlgeschlagen'
                    Logger.warning(f"PaymentBoxLayout: withdraw_used - payment time too long - {datetime.now()}")
                else:
                    self.information_label = 'Vielen Dank und \nbis bald.'
                    Logger.info(f"PaymentBoxLayout: withdraw_used - withdraw link was used - {datetime.now()}")
                Clock.schedule_once(self.payment_done, 5)

    def payment_done(self, _):
        '''The method is called after the payment was payed and switches back to the video screen.'''
        MDApp.get_running_app().root.ids.scrmanager.current = 'videoscreen'
        self.information_label = 'Bitte Bargeld \n einzahlen. '

    def get_lnurl_qrcode_img_path(self, lnurl):
        '''The method creates the img path for the lnurl qrcode.'''
        return f"qrcodes/{lnurl[-10:]}.png"

    def show_qr_code(self, lnurl):
        '''The method presents the lnurl qr code on the payment screen.'''
        self.create_qrcode_img(lnurl)
        img_path = self.get_lnurl_qrcode_img_path(lnurl)
        self.image_path = img_path
        MDApp.get_running_app().root.ids.image_id.opacity = 1
        Logger.info(f"PaymentBoxLayout: show_qr_code - image_path now {self.image_path} - {datetime.now()}")

    def create_qrcode_img(self, lnurl):
        '''The method creates a qr-code and stores the image in the current directory.'''
        qr = qrcode.QRCode()
        qr.add_data(lnurl.upper())
        img = qr.make_image(back_color=(0, 0, 0), fill_color=(255, 153, 0))
        img_path = self.get_lnurl_qrcode_img_path(lnurl)
        img.save(img_path)
        Logger.info(f"PaymentBoxLayout: create_qr_code - qr-code created - {datetime.now()}")


    def setup_cash_acceptor(self):
        '''The method initialises the parameters of the cash acceptor.'''
        self.biller.channels_set(self.biller.CH_ALL)
        self.biller.display_enable()
        self.biller.enable()
        Logger.info(f"PaymentBoxLayout: setup_cash_acceptor - SN {self.biller.serial:08X} enabled - {datetime.now()}")

    def disable_cash_acceptor(self):
        '''The method disables the cash acceptor and resets the parameters.'''
        self.biller.disable()
        self.biller.display_disable()
        self.biller.channels_set(None)
        Logger.info(f"PaymentBoxLayout: disable_cash_acceptor - biller disabled - {datetime.now()}")


class MyApp(MDApp):
    '''The main kivymd app.'''

    def build(self):
        '''The method builds the application based on the kivy file.'''
        return Builder.load_file("main.kv")


if __name__ == '__main__':
    MyApp().run()
