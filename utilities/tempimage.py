import uuid
import os

# creating image with random name and function for its deletion (used for caching images on disk and deleting them after email has been sent)
class TempImage:
    def __init__(self, basePath="./", ext=".jpg"):
        # construct the file path
        self.name = str(uuid.uuid4())
        self.path = "{base_path}/{rand}{ext}".format(base_path=basePath,
                                                     rand=self.name, ext=ext)

    def cleanup(self):
        # remove the file
        os.remove(self.path)
