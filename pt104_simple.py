import ctypes
import numpy as np
import time

temp1 = np.zeros((1,), dtype=np.int32)
temp2 = np.zeros((1,), dtype=np.int32)
temp3 = np.zeros((1,), dtype=np.int32)
temp4 = np.zeros((1,), dtype=np.int32)
details = np.zeros((10,), dtype=np.int8)
length = np.zeros((10,), dtype=np.uint32)

try:
    mydll = ctypes.windll.LoadLibrary('usbpt104')
except WindowsError:
    raise ImportError('usbpt104.dll not found. Check driver is installed.')

# mydll = ctypes.windll.LoadLibrary('UsbPt104.dll')
handlePointer = ctypes.c_short()
# temp=np.zeros((9,),dtype=np.int64)


status_unit = mydll.UsbPt104OpenUnit(ctypes.byref(handlePointer), 0)
# mydll.UsbPt104Enumerate(details.ctypes.data,length.ctypes.data,'CT_USB')

print ('open unit status:', status_unit)
#print ('USB:', details)

for j in range(1, 4):
    status_channel = mydll.UsbPt104SetChannel(handlePointer, j, 1, 2)
    print ('open channel status', status_channel)

def pid(temp):
    p = 5
    sp = 20
    duty_cycle = p*(temp - sp)
    return duty_cycle

for i in range(0, 500):
    mydll.UsbPt104GetValue(handlePointer, 1, temp1.ctypes.data, False)
    mydll.UsbPt104GetValue(handlePointer, 2, temp2.ctypes.data, False)
    mydll.UsbPt104GetValue(handlePointer, 3, temp3.ctypes.data, False)
    dc = pid(temp2[0] / 1000.0)
    print (temp1 / 1000.0, temp2 / 1000.0, temp3 / 1000.0, dc,'%')

    time.sleep(0.1)