import cv2

cap= cv2.VideoCapture('udp://192.168.8.109:4747')

while True:
    frame, img = cap.read()
    img =cv2.resize(img, (620,480))
    cv2.imshow("123",img)

