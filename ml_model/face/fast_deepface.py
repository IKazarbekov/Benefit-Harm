import cv2
from deepface import DeepFace

# Делаем снимок
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
cap.release()

if not ret:
    print("Не удалось снять фото")
else:
    # Анализируем
    result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
    emotion = result[0]['dominant_emotion']
    print(f"Настроение: {emotion}")