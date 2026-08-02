import cv2
from deepface import DeepFace

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        break

    try:
        result = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)

        # DeepFace mikone list bede age chandin sourat bashe
        if isinstance(result, list):
            faces = result
        else:
            faces = [result]

        for face in faces:
            region = face['region']
            x, y, w, h = region['x'], region['y'], region['w'], region['h']

            dominant_emotion = face['dominant_emotion']
            emotion_scores = face['emotion']

            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2)
            cv2.putText(img, dominant_emotion, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    except Exception as e:
        pass  # agar sourat peida nashod, khata nade

    cv2.imshow("Emotion Detection", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()