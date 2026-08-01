import os

import apps.PC.utils.camera as camera

def test_snapshot():
    camera.snapshot("test_image.png")

    assert os.path.isfile("test_image.png")

    os.remove("test_image.png")