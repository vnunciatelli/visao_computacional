import cv2
import mediapipe as mp
import pyserial

arduino = serial.Serial(port='COM4', baudrate=115200, timeout=.1)
wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

class handDetector():
    def __init__(self, mode = False, maxHands = 2, detectionCon = 0.5, trackCon = 0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        self.detectionCon, self.trackCon)
        self.mpdraw = mp.solutions.drawing_utils


    def findHands(self, img, draw = True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handlms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpdraw.draw_landmarks(img, handlms, self.mpHands.HAND_CONNECTIONS)
        return img


    def findPosition(self, img, handNo = 0, draw = True):
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]

            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
        #print(lmList)
        return lmList

detector = handDetector()
tipIds = [4, 8, 12, 16, 20]


def Right_hand():
    right_fingers_count = 0
    if lmList[tipIds[4]][1] > lmList[tipIds[3]][1]:  # right hand

        for id1 in range(1, 5):
            if lmList[tipIds[id1]][2] < lmList[tipIds[id1] - 2][2]:
                right_fingers.append(1)

            else:
                right_fingers.append(0)
        if lmList[tipIds[0]][1] < lmList[tipIds[0] - 1][1]:
            right_fingers.append(1)

        else:
            right_fingers.append(0)

        right_fingers_count = right_fingers.count(1)
    return right_fingers_count


def Left_hand():
    left_fingers_count = 0
    if lmList[tipIds[4]][1] < lmList[tipIds[3]][1]:  # left hand

        for id2 in range(1, 5):
            if lmList[tipIds[id2]][2] < lmList[tipIds[id2] - 2][2]:
                left_fingers.append(1)

            else:
                left_fingers.append(0)
        if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
            left_fingers.append(1)

        else:
            left_fingers.append(0)

        left_fingers_count = left_fingers.count(1)
    return left_fingers_count

while True:
    _, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        right_fingers = []
        left_fingers = []

        totalRightFingers = Right_hand()
        totalLeftFingers = Left_hand()
        print(totalRightFingers)
        print(totalLeftFingers)

        totalFingers = totalRightFingers + totalLeftFingers
        arduino.write(bytes(str(totalFingers), 'utf-8'))

    cv2.imshow("DISPLAY", img)
    cv2.waitKey(1)
