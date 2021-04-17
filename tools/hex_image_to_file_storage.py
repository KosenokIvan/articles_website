from io import BytesIO
from werkzeug.datastructures import FileStorage


def hex_image_to_file_storage(hex_image):
    return FileStorage(BytesIO(bytes.fromhex(hex_image)), "qq.png")
