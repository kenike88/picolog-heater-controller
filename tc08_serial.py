import serial, time
i = 0

ser = serial.Serial('COM4',9600, timeout=1)

print(ser.isOpen())

time.sleep(1)
while(i <100):
    hello = ser.readline()
    print(str(hello))
    i += i
ser.close()
