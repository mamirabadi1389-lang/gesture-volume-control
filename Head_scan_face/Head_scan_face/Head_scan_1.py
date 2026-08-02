import cv2
from deepface import DeepFace
import pandas as pd
from datetime import datetime
import os

KNOWN_FACES_DB = "known_faces"
LOG_PATH = "logs/emotion_log.csv"
os.makedirs("logs", exist_ok=True)

# age dade shode be in shekle model: emotion, age, gender ba detector daghigh
ACTIONS = ['emotion', 'age', 'gender']
DETECTOR_BACKEND = "retinaface"  # daghigh tarin detector

log_data = []

cap = cv2.VideoCapture(0)

print("Baraye khorooj 'q' ro bezan. Baraye zakhireye log 's' ro bezan.\n")

while True:
    success, img = cap.read()
    if not success:
        print("Khata: natoonestam az doorbin frame begiram.")
        break

    try:
        results = DeepFace.analyze(
            img,
            actions=ACTIONS,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=False,
            align=True
        )

        if isinstance(results, dict):
            results = [results]

        for face in results:
            region = face['region']
            x, y, w, h = region['x'], region['y'], region['w'], region['h']

            if w == 0 or h == 0:
                continue  # sourat vaghei peida nashode

            dominant_emotion = face['dominant_emotion']
            emotion_conf = face['emotion'][dominant_emotion]
            age = face['age']
            gender = face['dominant_gender']
            gender_conf = face['gender'][gender]

            # --- tashkhise hoviat ---
            identity_name = "Unknown"
            try:
                face_crop = img[y:y+h, x:x+w]
                find_result = DeepFace.find(
                    face_crop,
                    db_path=KNOWN_FACES_DB,
                    model_name="ArcFace",
                    detector_backend=DETECTOR_BACKEND,
                    enforce_detection=False,
                    silent=True
                )

                if len(find_result) > 0 and len(find_result[0]) > 0:
                    best_match_path = find_result[0].iloc[0]['identity']
                    identity_name = os.path.basename(os.path.dirname(best_match_path))
            except Exception:
                pass

            # --- rasm rooye tasvir ---
            label = f"{identity_name} | {dominant_emotion} ({emotion_conf:.0f}%)"
            label2 = f"{gender} ({gender_conf:.0f}%) | Age: {age}"

            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2)
            cv2.putText(img, label, (x, y - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(img, label2, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # --- zakhire baraye log ---
            log_data.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "identity": identity_name,
                "emotion": dominant_emotion,
                "emotion_confidence": round(emotion_conf, 2),
                "age": age,
                "gender": gender,
                "gender_confidence": round(gender_conf, 2)
            })

    except Exception as e:
        print(f"Khata dar tahlil: {e}")

    cv2.imshow("Face Analysis", img)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("s"):
        df = pd.DataFrame(log_data)
        df.to_csv(LOG_PATH, index=False, encoding="utf-8-sig")
        print(f"Log zakhire shod: {LOG_PATH} ({len(log_data)} radif)")

cap.release()
cv2.destroyAllWindows()

# zakhireye khodkar moghe khoroj ham
if log_data:
    df = pd.DataFrame(log_data)
    df.to_csv(LOG_PATH, index=False, encoding="utf-8-sig")
    print(f"Log nahaei zakhire shod: {LOG_PATH} ({len(log_data)} radif)")