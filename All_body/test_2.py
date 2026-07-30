import cv2
import mediapipe as mp

mpHolistic = mp.solutions.holistic
holistic = mpHolistic.Holistic(
    model_complexity=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mpDraw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        break

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = holistic.process(imgRGB)

    # rasme badan
    if result.pose_landmarks:
        mpDraw.draw_landmarks(img, result.pose_landmarks, mpHolistic.POSE_CONNECTIONS)

    # rasme dast chap
    if result.left_hand_landmarks:
        mpDraw.draw_landmarks(img, result.left_hand_landmarks, mpHolistic.HAND_CONNECTIONS)

    # rasme dast rast
    if result.right_hand_landmarks:
        mpDraw.draw_landmarks(img, result.right_hand_landmarks, mpHolistic.HAND_CONNECTIONS)

    # rasme surat (ekhtiari, kheili shologhe)
    if result.face_landmarks:
        mpDraw.draw_landmarks(img, result.face_landmarks, mpHolistic.FACEMESH_CONTOURS)

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()