import cv2
import mediapipe as mp
import math
import numpy as np

from pycaw.pycaw import AudioUtilities

device = AudioUtilities.GetSpeakers()
volume = device.EndpointVolume

# volume.GetMute()
# volume.GetMasterVolumeLevel()
# volume.GetVolumeRange()
#volume.SetMasterVolumeLevel(-20, None)


cap = cv2.VideoCapture(0)
mpHands = mp.solutions.hands
hands = mpHands.Hands()

MENU = """
╔════════════════════════════════╗
║        Hand Gesture Menu        ║
╠════════════════════════════════╣
║  1. Namayeshe chehre             ║
║  2. Control ba dast              ║
║  3. Khorooj                      ║
╚════════════════════════════════╝
"""

def show_face():
    print("\n[Namayeshe tasvire doorbin faal shod] Baraye khorooj 'q' ro bezan ya panjereh ro bebandi.\n")
    while True:
        success, img = cap.read()
        if not success:
            print("Khata: natoonestam az doorbin frame begiram.")
            break

        cv2.imshow("Image", img)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyWindow("Image")


def control_with_hand():
    print("\n[Halate control ba dast faal shod] Baraye khorooj 'q' ro bezan.\n")
    while True:
        success, img = cap.read()
        if not success:
            print("Khata: natoonestam az doorbin frame begiram.")
            break

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = hands.process(imgRGB)

        if result.multi_hand_landmarks:
            hand = result.multi_hand_landmarks[0]
            mp.solutions.drawing_utils.draw_landmarks(
                                img,
                                hand,
                                mpHands.HAND_CONNECTIONS
                            )
            lmList = []
            for id , lm in enumerate(hand.landmark):
                h,w,c = img.shape
                cx , cy = int(lm.x*w), int(lm.y*h)
                lmList.append([id,cx,cy])

            if len(lmList):
                    x1 ,y1 =lmList[4][1],lmList[4][2]
                    x2 ,y2 =lmList[8][1],lmList[8][2]

                    cx,cy = (x1 + x2) // 2,(y1 + y2)//2

                    cv2.circle(img, (x1, y1),5 ,(255,255,0),cv2.FILLED)
                    cv2.circle(img, (x2, y2),5 ,(255,255,0),cv2.FILLED)
                    cv2.circle(img, (cx, cy),5 ,(255,255,0),cv2.FILLED)
                    cv2.line(img , (x1,y1) ,(x2 ,y2), (255,255,0),3)

                    length = int(math.hypot(x2 -x1 - y1))


                    handRange = [50, 400]

                    vol = int(np.interp(length , handRange , [0 , -64]))
                    volume.SetMasterVolumeLevel(vol, None)
                    
                    #print(length)

        cv2.imshow("Image", img)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyWindow("Image")


def main():
    while True:
        print(MENU)
        raw_choice = input("Entekhabeto vared kon -> ").strip()

        if not raw_choice.isdigit():
            print("Lotfan faghat adad vared kon (1, 2 ya 3).\n")
            continue

        choice = int(raw_choice)

        if choice == 1:
            show_face()
        elif choice == 2:
            control_with_hand()
        elif choice == 3:
            print("Dar hale khorooj...")
            break
        else:
            print("Entekhabe namotabar! Faghat 1, 2 ya 3 ro vared kon.\n")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()