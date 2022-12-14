import serial.tools.list_ports
a=serial.tools.list_ports.comports()
print(a[0])