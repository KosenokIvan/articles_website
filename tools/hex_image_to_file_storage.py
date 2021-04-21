from io import BytesIO
from werkzeug.datastructures import FileStorage
from tools.errors import IncorrectImageError


def hex_image_to_file_storage(hex_image):
    try:
        return FileStorage(BytesIO(bytes.fromhex(hex_image)), "qq.png")
    except Exception:
        raise IncorrectImageError
