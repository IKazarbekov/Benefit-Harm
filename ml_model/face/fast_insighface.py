from insightface.app import FaceAnalysis
import cv2, os

def analyze_face_male_age_by_file(img: str):
    """
    read image and detect male, age by face
    :param img: path to image
    :return: is_male: bool, age
    """
    assert isinstance(img, str)
    assert os.path.exists(img)

    app = FaceAnalysis(name='buffalo_l')
    app.prepare(ctx_id=-1)
    img = cv2.imread(img)
    faces = app.get(img)
    if len(faces) > 0:
        face = faces[0]
        is_male = face.gender == 1
        age = face.age
        return is_male, age
    else:
        raise Exception("Face not found")