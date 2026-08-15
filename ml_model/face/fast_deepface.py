import cv2
from deepface import DeepFace

# Делаем снимок
def get_mood(cap = cv2.VideoCapture(0)):
    ret, frame = cap.read()

    if not ret:
        raise Exception("Video capture failed")
    else:
        # Анализируем
        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        emotion = result[0]['dominant_emotion']
        return emotion