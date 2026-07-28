import cv2
import mediapipe as mp
import math
import numpy as np

from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# --- بخش صدا (اصلاح‌شده برای هر دو نسخه‌ی جدید و قدیم pycaw) ---
device = AudioUtilities.GetSpeakers()
try:
    # نسخه‌های جدید pycaw: پراپرتی مستقیم EndpointVolume
    volume = device.EndpointVolume
except AttributeError:
    # نسخه‌های قدیمی‌تر pycaw: باید خودمون Activate کنیم
    interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)

# volume.GetMute()
# volume.GetMasterVolumeLevel()
# volume.GetVolumeRange()
# volume.SetMasterVolumeLevel(-20, None)


cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("دوربین باز نشد. شماره دوربین یا اتصال آن را بررسی کنید.")

mpHands = mp.solutions.hands
hands = mpHands.Hands()


while True:

    success, img = cap.read()

    if not success:
        # اگر فریم نگرفت، این دور را رد کن به‌جای کرش کردن
        continue

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:

        hand = results.multi_hand_landmarks[0]

        mp.solutions.drawing_utils.draw_landmarks(img, hand, mpHands.HAND_CONNECTIONS)

        lmList = []

        for id, lm in enumerate(hand.landmark):

            h, w, c = img.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            lmList.append([id, cx, cy])

        if len(lmList) > 0:
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            cv2.circle(img, (x1, y1), 10, (255, 255, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (255, 255, 0), cv2.FILLED)
            cv2.circle(img, (cx, cy), 10, (255, 255, 0), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 0), 3)

            length = int(math.hypot(x2 - x1, y2 - y1))

            handRange = [50, 300]

            vol = int(np.interp(length, handRange, [-64, 0]))

            volume.SetMasterVolumeLevel(vol, None)

            # print(length)

    cv2.imshow("Image", img)

    # با کلید ESC یا q از حلقه خارج شو (قبلاً هیچ راه خروجی نداشت)
    key = cv2.waitKey(1) & 0xFF
    if key == 27 or key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
