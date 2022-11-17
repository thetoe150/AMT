def uart_write(data):
    ser.write((str(data) + "#").encode())
    return
