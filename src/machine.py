"""
The purpose of this module is to emulate the machine module of the ESP32 chip.  The primary reason to 
emulate the chip is for test-driving code (TDD).

Verified Firmware version: esp32-20190610-v1.11-37-g62f004ba4

Portions also tested with esp8266-20190529-v1.11
"""
import time

EMULATION_MODE = True

__author__ = "Todd Flanders https://github.com/tflander/Esp32IotKata"

expectedPulseTimeForTesting = 0
expectedPulseTimeErrorForTesting = None
expectedTimeSleepMs = []
expectedTimeSleepUs = []
reset_called_for_testing = False


def resetExpectationsForTesting():
    global expectedPulseTimeForTesting
    global expectedPulseTimeErrorForTesting
    global expectedTimeSleepMs
    global expectedTimeSleepUs
    global reset_called_for_testing

    expectedPulseTimeForTesting = 0
    expectedPulseTimeErrorForTesting = None
    expectedTimeSleepMs = []
    expectedTimeSleepUs = []
    reset_called_for_testing = False


# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
def time_pulse_us(pin, pulse_level, timeout_us):
    global expectedPulseTimeErrorForTesting
    if expectedPulseTimeErrorForTesting is not None:
        raise TypeError(
            "expectedPulseTimeErrorForTesting"
        )  # pylint: disable=raising-bad-type

    pulse_time = expectedPulseTimeForTesting

    if type(pulse_time) == int:
        return pulse_time
    else:
        if not pulse_time:
            raise Exception(
                "unexpected call to time_pulse_us on empty expectation list"
            )
        raise TypeError('pulse_time')


def reset():
    global reset_called_for_testing
    reset_called_for_testing = True


def sleep_us_for_monkey_patching(delayUs):
    time.sleep(delayUs / 1000000)
    expectedTimeSleepUs.append(delayUs)


def sleep_ms_for_monkey_patching(delayMs):
    time.sleep(delayMs / 1000)
    expectedTimeSleepMs.append(delayMs)

irq_list = {}
class Pin:
    IN = "in"
    OUT = "out"
    IRQ_RISING = 'rising'
    IRQ_FALLING = 'falling'

    def resetExpectationsForTesting(self):
        self.triggerValuesForTesting = []

    # noinspection PyUnusedLocal,PyUnusedLocal
    def __init__(self, pin, mode=OUT, pull=None):
        self.currentStateForTesting = 0
        self.pinForTesting = pin
        self.triggerValuesForTesting = []
        self.resetExpectationsForTesting()
        self.irq_mode = self.IRQ_RISING

    def on(self):
        self.currentStateForTesting = 1
        self.triggerValuesForTesting.append(self.currentStateForTesting)
        global irq_list
        if irq_list[self.pinForTesting] and self.irq_mode == self.IRQ_RISING:
            irq_list[self.pinForTesting](self)

    def off(self):
        self.currentStateForTesting = 0
        self.triggerValuesForTesting.append(self.currentStateForTesting)
        if irq_list[self.pinForTesting] and self.irq_mode != self.IRQ_RISING:
            irq_list[self.pinForTesting](self)

    def value(self, newValue=None):
        if newValue == 0:
            self.off()
        elif newValue == 1:
            self.on()
        if self.currentStateForTesting is None:
            raise Exception(
                "Checking Value of Uninitialized OUT Pin.  Set the value before checking."
            )
        return self.currentStateForTesting
    def irq(self,trigger,handler):
        global irq_list
        irq_list[self.pinForTesting]=handler
        pass


class Timer:

    PERIODIC = 0

    def __init__(self, id):
        self.timer_id_for_testing = id
        self.is_running_for_testing = False

    def deinit(self):
        self.is_running_for_testing = False

    def init(self, period, mode=PERIODIC, callback=None):
        self.is_running_for_testing = True

class ADC:
    def __init__(self, pin):
        self.pinForTesting = pin

    def read(self):
        import random

        return int(random.random() * 1024)


def unique_id():
    import uuid

    return str(uuid.uuid4())
