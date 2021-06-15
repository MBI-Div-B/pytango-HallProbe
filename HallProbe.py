#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Schick, Borchert
# Adaptation of the code from
# https://pytango.readthedocs.io/en/stable/quicktour.html
# with the example from
# https://github.com/pimoroni/ads1015-python/tree/master/examples

import time
import numpy
import tango
from tango import DebugIt, DeviceProxy
from tango.server import run
from tango.server import Device, DeviceMeta
from tango.server import attribute, command, pipe
from tango.server import class_property, device_property
from tango import AttrQuality,DispLevel, DevState
from tango import AttrWriteType, PipeWriteType

from ads1015 import ADS1015

class HallProbe(Device, metaclass = DeviceMeta):
    
    #__metaclass__ = DeviceMeta
    
    magneticField = attribute(
        label="magneticField",
        dtype="float",
        access=AttrWriteType.READ,
        unit="mT",
        format="%8.4f",
        doc="The hall probe voltage converted to magnetic field by one of three calibration functions matching the three hardware switch settings."
        )

    info = pipe(label='Info')

    host = device_property(dtype=str)
    port = device_property(dtype=int, default_value=9788)

    def init_device(self):
        Device.init_device(self)
        
        self.__ads1015 = ADS1015()
        self.__ads1015.set_mode('single')
        self.__ads1015.set_programmable_gain(2.048)
        self.__ads1015.set_sample_rate(1600)
        self.__channel = 'in0/ref'
        self.__reference = self.__ads1015.get_reference_voltage()
        self.__voltage = 0
        self.__measRange = 3
        self.__calibrations = [[0.010332, 0.016412],[0.021562, 0.08932],[0.095927, 0.196237]]
        #                         V/mT      +V          V/mT     +V        V/mT      + V
        #                      10V =  1T               10V = 0.5T        9.6V = 104mT
        
        
        self.set_state(DevState.ON)
        print('Initialised')
    
    @command(dtype_in=int)    
    def set_measRange(self, argin):
        if argin in [1,2,3]:
            self.__measRange = int(argin)
        
    @command(dtype_out=int)    
    def get_measRange(self):
        return self.__measRange 
        
    @command (dtype_out='float', polling_period= 100)  
    def get_voltage(self):        
        self.__voltage = float(self.__ads1015.get_compensated_voltage(channel=self.__channel, reference_voltage=self.__reference))
        #print('Voltage was updated to %.5f V.'%voltage)
        return self.__voltage
    
    def read_magneticField(self):
        m, c = self.__calibrations[(self.__measRange -1)]
        #print('%.3f mT'%self.magneticFieldValue)
        return (self.__voltage - c)/m

    def read_info(self):
        return 'Information', dict(manufacturer='Tango',
                                   model='PS2000',
                                   version_number=123)

    @command
    def TurnOn(self):
        self.set_state(DevState.ON)

    @command
    def TurnOff(self):
        self.set_state(DevState.OFF)


if __name__ == "__main__":
    HallProbe.run_server()