import sys
from io import BytesIO

from PIL import Image as PILImage
from django.core.files.uploadedfile import InMemoryUploadedFile


def compress_image(image):
    image_temp = PILImage.open(image)
    orig_size = image.file.size
    if orig_size > 1000000:
        quality = int((100 * 1000000) / image.file.size)
        output = BytesIO()
        temp = image_temp.resize((1020, 573))
        image_temp.save(output, format='JPEG', quality=quality)
        output.seek(0)
        image = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % image.name.split('.')[0],
                                     'image/jpeg', sys.getsizeof(output), None)
    return image
