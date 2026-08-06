import ml_model.face.fast_insighface as fast_insighface

def test_analyze_face():
    is_male, age = fast_insighface.analyze_face_male_age_by_file("face_image_for_test.png")
    assert is_male == True
    assert 50 > age > 10