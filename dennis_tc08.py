#!/usr/bin/env python
# coding: utf8
# Change Log:
# 01/08/16:
# Use tc-08 channel 1 as the heater feedback sensor. Currently, this version only support a pure P control. I and D will be implemented later.

from tc08usb import TC08USB, USBTC08_ERROR, USBTC08_UNITS, USBTC08_TC_TYPE
import time

tc08usb = TC08USB()
tc08usb.open_unit()
tc08usb.set_mains(50)
for i in range(1, 3):
    tc08usb.set_channel(i, USBTC08_TC_TYPE.K)
tc08usb.get_single()

ch_num = int(input("How many channels are you using? >> "))
setpoint = int(input("What is your temperature setpoint? >> "))
p_gain = int(input("What is your P gain value? >> "))


def PWM(temp):
    duty_cycle = temp * p_gain
    if duty_cycle > 90:
        duty_cycle = 100
    elif duty_cycle < 10:
        duty_cycle = 0

    return duty_cycle


while 1:
    tc08usb.get_single()
    d_temp = setpoint - tc08usb[1]
    dc = PWM(d_temp)
    for i in range(1, ch_num + 1):
        print("%d: %f" % (i, tc08usb[i]))
    s = "Duty Cycle:" + str(dc) + "%"
    print(s)
    time.sleep(0.5)

tc08usb.close_unit()
