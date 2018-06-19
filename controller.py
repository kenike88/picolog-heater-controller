# Written By: Dennis Ong
# This is a heater controller program that uses Arduino to control a relay based on temperature readings from Picolog TC08 and PT104.

import ctypes
import numpy as np
from tc08usb import TC08USB, USBTC08_ERROR, USBTC08_UNITS, USBTC08_TC_TYPE
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import serial
import struct
import time as tt


from pyqtgraph.ptime import time

uiFile = 'controllerUI.ui'
WindowTemplate, TemplateBaseClass = pg.Qt.loadUiType(uiFile)


#========================= Controller Setup ===========================================

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

ser_comm = 'COM'+str(arduino_comm)
ser = serial.Serial(ser_comm, 9600)
print(ser.name)
print(ser.isOpen())
tt.sleep(5)

#======================= PT-104 Initialisation ========================================

temp = np.zeros((1,), dtype=np.int32) #arrays for channel 1 - 4 to store measurements
rtd_array = np.zeros((rtd_ch_num,), dtype=np.int32)
#temp_array = np.zeros((tc_ch_num + rtd_ch_num,), dtype=np.float64)

temp_array = []
tc1 = []
tc2 = []
rtd1 = []
temp_hist = np.zeros((tc_ch_num + rtd_ch_num,),dtype=np.float64)
tc_read = 0
tc_init_flag = 0
x = np.zeros((rtd_ch_num + tc_ch_num,), dtype=np.int)
total_ch = tc_ch_num + rtd_ch_num

data = [[] for _ in range(total_ch)]

try:
    mydll = ctypes.windll.LoadLibrary('usbpt104')
except WindowsError:
    raise ImportError('usbpt104.dll not found. Check driver is installed.')

handlePointer = ctypes.c_short()
status_unit = mydll.UsbPt104OpenUnit(ctypes.byref(handlePointer), 0)

print ('open unit status:', status_unit)
for j in range(1, rtd_ch_num+1):
    status_channel = mydll.UsbPt104SetChannel(handlePointer, j, 1, 2)
    print('open channel status', status_channel)

# ======================= TC-08 Initialisation ===========================================
tc08usb = TC08USB()

while tc_init_flag == 0: #sometimes there is error setting the TC channels. if so, reset the channels.
    tc08usb.open_unit()
    tc08usb.set_mains(50)
    for i in range(1, tc_ch_num+1):
        tc08usb.set_channel(i, USBTC08_TC_TYPE.K)

    for i in range(0, 10):
        tc_gs_status = tc08usb.get_single() # returns 1 for successful reading
        print("TC Flag",i,tc_gs_status)
        tc_read += tc_gs_status
        if tc_read == tc_ch_num:
            tc_init_flag = 1

pwm_data = 60
ser_data = pwm_data.to_bytes(2, byteorder='little')
test = ser.write(struct.pack('>B',60 ))
print("Sent to arduino",test)


# ======================= PID =============================================================
def pid(temp):
    p = p_gain
    sp = setpoint
    duty_cycle = p * (sp - temp)
    return duty_cycle

# ================================ QT Graph initialisation =================================
#QtGui.QApplication.setGraphicsSystem('raster')
app = QtGui.QApplication([])
#mw = QtGui.QMainWindow()
#mw.resize(800,800)

p = pg.plot()
p.setWindowTitle('pyqtgraph example: MultiPlotSpeedTest')
#p.setRange(QtCore.QRectF(0, -10, 5000, 20))
p.setLabel('bottom', 'Index', units='B')

# Enable antialiasing for prettier plots
#pg.setConfigOptions(antialias=True)

curves = []
for ch in range(total_ch):
    c = pg.PlotCurveItem(pen=(ch, total_ch*3))
    p.addItem(c)
    curves.append(c)
ptr = 0


def update():
    global curves, data, ptr, p, temp_array, temp_hist, x, y, rtd_ch_num,rtd_array, tc1, tc2, rtd1, mydll, handlePointer
    #mydll = ctypes.windll.LoadLibrary('UsbPt104.dll')
    #handlePointer = ctypes.c_short()


    for j in range(1,rtd_ch_num+1):
        pt_gv_status = mydll.UsbPt104GetValue(handlePointer, j, temp.ctypes.data, False)
    print ('PT GV', pt_gv_status)
    if pt_gv_status == 0 or pt_gv_status == 280:
        rtd_array[j - 1] = temp[0]
    else:
        rtd_array[j - 1] = 0

    tc08usb.get_single()

    if pid_selector == 1: # TC selected as
        dc = pid(tc08usb[1] / 1000.0)
    elif pid_selector == 2:
        dc = pid(rtd_array[0] / 1000.0)
    else:
        dc = 0

    for i1 in range(0, tc_ch_num+1):
        if i1 != 0:
            print("TC"+str(i1)+": ",tc08usb[i1])
            temp_array = np.append(temp_array,tc08usb[i1])
            data[i1].append(tc08usb[i1])


        # if i1 == 2:
        #     tc2 = np.append(tc2, tc08usb[i1])
        #     data[i1] = np.append(data, tc1)

    for i2 in range(0,rtd_ch_num):
        print("RTD" + str(i2+1) +": ", rtd_array[i2] / 1000.0)
        temp_array = np.append(temp_array,rtd_array[i2] / 1000.0)
        data[tc_ch_num - 1 + i2].append(rtd_array[i2] / 1000.0)

    for ii in range(total_ch):
        curves[ii].setData(data[ii])

    print("Duty Cycle: ", dc, "%")

    print("Temporary Array: \n", temp_array)
    temp_hist = np.vstack((temp_hist,temp_array))
    temp_array = []
    y = np.full((rtd_ch_num+tc_ch_num,),i, dtype=np.int)
    x = np.vstack((x,y))


    if ptr == 0:
        p.enableAutoRange('xy', True)  ## stop auto-scaling after the first data set is plotted
    ptr += 1

# for i in range(0, loop_num):

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)

#p.nextRow()

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

