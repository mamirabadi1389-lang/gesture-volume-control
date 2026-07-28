import cv2
import mediapipe as mp

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
            for hand in result.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    img,
                    hand,
                    mpHands.HAND_CONNECTIONS
                )

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