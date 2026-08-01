import cv2

def snapshot(filename: str):
    """
    Connect to camera and take a snapshot
    :param filename: file path for save image
    :return: None
    """
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        raise IOError("Cannot open webcam")
    ret, frame = cam.read()
    if ret:
        cv2.imwrite(filename, frame)
    else:
        raise IOError("Snapshot failed")

if __name__ == "__main__":
    snapshot("test_snapshot.png")