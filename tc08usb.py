#!/usr/bin/env python
# coding: utf8

from enum import Enum # use enum34 for Python 2
import six
import ctypes
import numpy as np
import os

class USBTC08_ERROR(Enum):
    OK = 0
    OS_NOT_SUPPORTED = 1
    NO_CHANNELS_SET = 2
    INVALID_PARAMETER = 3
    VARIANT_NOT_SUPPORTED = 4
    INCORRECT_MODE = 5
    ENUMERATION_INCOMPLETE = 6
    NOT_RESPONDING = 7
    FW_FAIL = 8
    CONFIG_FAIL = 9
    NOT_FOUND = 10
    THREAD_FAIL = 11
    PIPE_INFO_FAIL = 12
    NOT_CALIBRATED = 13
    PICOPP_TOO_OLD = 14
    COMMUNICATION = 15

    @classmethod
    def help(cls, error):
        d = {
            USBTC08_ERROR.OK: "No error occurred.",
            USBTC08_ERROR.OS_NOT_SUPPORTED: "The driver supports Windows XP SP3, Windows Vista, Windows 7 and Windows 8.",
            USBTC08_ERROR.NO_CHANNELS_SET: "A call to usb_tc08_set_channel() is required.",
            USBTC08_ERROR.INVALID_PARAMETER: "One or more of the function arguments were invalid.",
            USBTC08_ERROR.VARIANT_NOT_SUPPORTED: "The hardware version is not supported. Download the latest driver.",
            USBTC08_ERROR.INCORRECT_MODE: "An incompatible mix of legacy and non-legacy functions was called (or usb_tc08_get_single() was called while in streaming mode.)",
            USBTC08_ERROR.ENUMERATION_INCOMPLETE: "usb_tc08_open_unit_async() was called again while a background enumeration was already in progress.",
            USBTC08_ERROR.NOT_RESPONDING: "Cannot get a reply from a USB TC-08.",
            USBTC08_ERROR.FW_FAIL: "Unable to download firmware.",
            USBTC08_ERROR.CONFIG_FAIL: "Missing or corrupted EEPROM.",
            USBTC08_ERROR.NOT_FOUND: "Cannot find enumerated device.",
            USBTC08_ERROR.THREAD_FAIL: "A threading function failed.",
            USBTC08_ERROR.PIPE_INFO_FAIL: "Can not get USB pipe information.",
            USBTC08_ERROR.NOT_CALIBRATED: "No calibration date was found.",
            USBTC08_ERROR.PICOPP_TOO_OLD: "An old picopp.sys driver was found on the system.",
            USBTC08_ERROR.COMMUNICATION: "The PC has lost communication with the device."
        }
        return(d[error])

class USBTC08_UNITS(Enum):
    CENTIGRADE = 0
    FAHRENHEIT = 1
    KELVIN = 2
    RANKINE = 3

class USBTC08_TC_TYPE(Enum):
    DISABLED = " "
    B = "B"
    E = "E"
    J = "J"
    K = "K"
    N = "N"
    R = "R"
    S = "S"
    T = "T"

    @classmethod
    def ordinal(cls, tc_type):
        if isinstance(tc_type, Enum):
            tc_type = tc_type.value
        elif isinstance(tc_type, six.string_types):
            tc_type = tc_type.upper()
        return(ord(tc_type))


class TC08USB(object):
    def __init__(self, dll_path=""):
        dll_filename = os.path.join(dll_path, 'usbtc08.dll')
        self._dll = ctypes.windll.LoadLibrary(dll_filename)
        
        self._handle = None # handle for device
        
        self._temp = np.zeros( (9,), dtype=np.float32)
        self._overflow_flags = np.zeros( (1,), dtype=np.int16)
        
        self._units = USBTC08_UNITS.CENTIGRADE # 0:C 1:F 2:K 3:RK

    #def units(self, units):
    #    self._units = units
        
    def open_unit(self):
        self._handle = self._dll.usb_tc08_open_unit()
        return(self._handle)
        
    def set_mains(self, value=50):
        return(self._dll.usb_tc08_set_mains(self._handle, value))
        
    def set_channel(self, channel, tc_type):
        tc_type = USBTC08_TC_TYPE.ordinal(tc_type)
        return(self._dll.usb_tc08_set_channel(self._handle, channel, tc_type))

    def get_single(self):
        return(self._dll.usb_tc08_get_single(self._handle, self._temp.ctypes.data, self._overflow_flags.ctypes.data, self._units.value))

    def close_unit(self):
        return(self._dll.usb_tc08_close_unit(self._handle))
        
    def __getitem__(self, channel):
        return(self._temp[channel])
