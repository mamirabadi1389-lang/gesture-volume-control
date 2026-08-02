import cv2
from fer import FER

detector = FER(mtcnn=True)
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        break

    result = detector.detect_emotions(img)

    if result:
        for face in result:
            (x, y, w, h) = face["box"]
            emotions = face["emotions"]
            top_emotion = max(emotions, key=emotions.get)

            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2)
            cv2.putText(img, top_emotion, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow("Emotion Detection", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()