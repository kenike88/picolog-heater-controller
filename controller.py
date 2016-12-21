# Written By: Dennis Ong
# This is a heater controller program that uses Arduino to control a relay based on temperature readings from Picolog TC08 and PT104.

import ctypes
import numpy as np
import time
from tc08usb import TC08USB, USBTC08_ERROR, USBTC08_UNITS, USBTC08_TC_TYPE

response = input("Do you wish to perform setup? y/n >>")

if response in ["y", "Y"]:
    tc_ch_num = int(input("How many TC08 channels are you using? >> "))
    rtd_ch_num = int(input("How many PT104 channels are you using? >> "))
    pid_selector = int(input("For PID control, use TC or RTD? For TC, press 1. For RTD, press 2>> "))
    arduino_comm = int(input("What is Arduino comm port? If 'COM3', input '3' >> "))
    relay_pin = int(input("What is relay's i/o pin number on Arduino?  >> "))
    setpoint = int(input("What is your temperature setpoint? >> "))
    p_gain = int(input("What is your P gain value? >> "))
else:
    print("proceeding")

#PT-104
temp1 = np.zeros((1,), dtype=np.int32)
temp2 = np.zeros((1,), dtype=np.int32) #arrays for channel 1 - 4 to store measurements
temp3 = np.zeros((1,), dtype=np.int32)
temp4 = np.zeros((1,), dtype=np.int32)
temp = np.zeros((1,), dtype=np.int32)
temp_array = np.zeros((4,), dtype=np.int32)
tc_read = 0
tc_init_flag = 0

mydll = ctypes.windll.LoadLibrary('UsbPt104.dll')
handlePointer = ctypes.c_short()
status_unit = mydll.UsbPt104OpenUnit(ctypes.byref(handlePointer), 0)

print ('open unit status:', status_unit)
for j in range(1, rtd_ch_num+1):
    status_channel = mydll.UsbPt104SetChannel(handlePointer, j, 1, 2)
    print('open channel status', status_channel)

#setup TC-08
tc08usb = TC08USB()

while tc_init_flag == 0: #sometimes there is error setting the TC channels. if so, reset the channels.
    tc08usb.open_unit()
    tc08usb.set_mains(50)
    for i in range(1, tc_ch_num):
        tc08usb.set_channel(i, USBTC08_TC_TYPE.K)
    for i in range(0, 10):
        tc_gs_status = tc08usb.get_single() # returns 1 for successful reading
        print("TC Flag",i,tc_gs_status)
        tc_read += tc_gs_status
        if tc_read == tc_ch_num:
            tc_init_flag = 1

def pid(temp):
    p = p_gain
    sp = setpoint
    duty_cycle = p * (sp - temp)
    return duty_cycle

for i in range(0, 500):
    for j in range(1,rtd_ch_num+1):
        pt_gv_status = mydll.UsbPt104GetValue(handlePointer, j, temp.ctypes.data, False)
        print ('PT GV', pt_gv_status)
        if pt_gv_status == 0 or pt_gv_status == 280:
            temp_array[j-1] = temp[0]
        else:
            temp_array[j-1] = 0

    tc08usb.get_single()

    if pid_selector == 1: # TC selected as
        dc = pid(tc08usb[0] / 1000.0)
    elif pid_selector == 2:
        dc = pid(temp_array[0] / 1000.0)
    else:
        dc = 0

    for i in range(0,tc_ch_num):
        print("TC"+str(i+1)+": ",tc08usb[i])
    for i in range(0,rtd_ch_num):
        print("RTD"+str(i+1)+": ", temp_array[i]/1000.0)

    print("Duty Cycle: ", dc, "%")

    #time.sleep(0.1)
