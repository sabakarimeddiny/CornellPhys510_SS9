import logging
log = logging.getLogger('')
log.addHandler(logging.NullHandler())

import sys
from time import sleep
import numpy as np

from pymeasure.instruments.keithley import Keithley2000
from pymeasure.instruments import Instrument
from pymeasure.log import console_log
from pymeasure.display.Qt import QtGui
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import (
    Procedure, FloatParameter, unique_filename, Results,
    IntegerParameter, Parameter, BooleanParameter
)

import mcculw
from mcculw import ul
from mcculw.enums import TempScale

import time


class SS9Procedure(Procedure):

    your_name = Parameter("Your Name", default='')
    field_strength = FloatParameter("Field Strength",  units='T', default=0)
    I_bias = BooleanParameter('Current Forward?', default=True)
    delay = FloatParameter('Delay Time', units='s', default=20)
    T_max = IntegerParameter('Maximum Temp.', units = 'K', default = 350)

    mm1_measurement = BooleanParameter('Voltage', default=True)
    mm1_range = FloatParameter('Range', units = 'SI', default = 1)
    mm1_address = Parameter("MM1 Address", default = '')

    mm2_measurement = BooleanParameter('Voltage', default=True)
    mm2_range = FloatParameter('Range', units = 'SI', default = 1)
    mm2_address = Parameter("MM2 Address", default = '')

    mm3_measurement = BooleanParameter('Voltage', default=True)
    mm3_range = FloatParameter('Range', units = 'SI', default = 1)
    mm3_address = Parameter("MM3 Address", default = '')

    mm4_measurement = BooleanParameter('Voltage', default=True)
    mm4_range = FloatParameter('Range', units = 'SI', default = 1)
    mm4_address = Parameter("MM4 Adress", default = '')

    DATA_COLUMNS = ['elapsed_time', 'T', 'MM1 Reading',
                    'MM2 Reading', 'MM3 Reading',
                    'MM4 Reading']

    def startup(self):
        log.info("Setting up Multimeters")
        self.mm1 = Keithley2000(self.mm1_address)
        self.mm2 = Keithley2000(self.mm2_address)
        self.mm3 = Keithley2000(self.mm3_address)
        self.mm4 = Keithley2000(self.mm4_address)

        if self.mm1_measurement:
            self.mm1.measure_voltage(self.mm1_range)
        else:
            self.mm1.measure_current(self.mm1_range)

        if self.mm2_measurement:
            self.mm2.measure_voltage(self.mm2_range)
        else:
            self.mm2.measure_current(self.mm2_range)

        if self.mm3_measurement:
            self.mm3.measure_voltage(self.mm3_range)
        else:
            self.mm3.measure_current(self.mm3_range)

        if self.mm4_measurement:
            self.mm4.measure_voltage(self.mm4_range)
        else:
            self.mm4.measure_current(self.mm4_range)

        log.info("Setting up Thermocouple")


        self.mm2.voltage_nplc = 1 # Integration constant to Medium
        self.mm3.voltage_nplc = 1 # Integration constant to Medium
        self.mm4.voltage_nplc = 1 # Integration constant to Medium
        sleep(2)

    def execute(self):
        log.info("Starting Measurement")
        #prev_T = read_T
        T_min = ul.t_in(0, 0, TempScale.KELVIN)
        T = T_min
        start_time = time.time()
        while T < self.T_max:
            sleep(self.delay)
            elapsed_time = time.time() - start_time

            if self.mm1_measurement:
                M1 = self.mm1.voltage
            else:
                M1 = self.mm1.current

            if self.mm2_measurement:
                M2 = self.mm2.voltage
            else:
                M2 = self.mm2.current

            if self.mm3_measurement:
                M3 = self.mm3.voltage
            else:
                M3 = self.mm3.current

            if self.mm4_measurement:
                M4 = self.mm4.voltage
            else:
                M4 = self.mm4.current
            T = ul.t_in(0, 0, TempScale.KELVIN)
            prog = int(100*np.abs((T - T_min)/(self.T_max - T_min)))
            self.emit("progress", prog)


            data = {
                'elapsed_time': elapsed_time,
                'T': T,
                'MM1 Reading': M1,
                'MM2 Reading': M2,
                'MM3 Reading': M3,
                'MM4 Reading': M4
            }

            self.emit('results', data)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break
            else:
                continue
    def shutdown(self):
        log.info("Finished")
