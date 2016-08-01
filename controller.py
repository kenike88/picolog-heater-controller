# Written By: Dennis Ong
# This is a heater controller program that uses Arduino to control a relay based on temperature readings from Picolog TC08 and PT104.

import ctypes
import numpy as np
import time
from tc08usb import TC08USB, USBTC08_ERROR, USBTC08_UNITS, USBTC08_TC_TYPE

#PT-104
temp1 = np.zeros((1,), dtype=np.int32) #arrays for channel 1 - 4 to store measurements
temp2 = np.zeros((1,), dtype=np.int32)
temp3 = np.zeros((1,), dtype=np.int32)
temp0 = np.int32

mydll = ctypes.windll.LoadLibrary('UsbPt104.dll')
handlePointer = ctypes.c_short()

status_unit = mydll.UsbPt104OpenUnit(ctypes.byref(handlePointer), 'CR944/112')

print 'open unit status:', status_unit
for j in range(1, 4):
    status_channel = mydll.UsbPt104SetChannel(handlePointer, j, 1, 2)
    print 'open channel status', status_channel

#setup TC-08
tc08usb = TC08USB()
tc08usb.open_unit()
tc08usb.set_mains(50)
for i in range(1, 3):
    tc08usb.set_channel(i, USBTC08_TC_TYPE.K)
tc08usb.get_single()



def pid(temp):
    p = 5
    sp = 20
    duty_cycle = p*(temp - sp)
    return duty_cycle

for i in range(0, 500):
    mydll.UsbPt104GetValue(handlePointer, 1, temp1.ctypes.data, False)
    mydll.UsbPt104GetValue(handlePointer, 2, temp2.ctypes.data, False)
    mydll.UsbPt104GetValue(handlePointer, 3, temp3.ctypes.data, False)
    tc08usb.get_single()
    dc = pid(temp2[0] / 1000.0)
    print("TC: %f" % (tc08usb[1]))
    print temp1 / 1000.0, temp2 / 1000.0, temp3 / 1000.0, dc ,'%'

    time.sleep(0.1)
