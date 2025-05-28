import os
from PIL import Image

def allowed_image(filename, fileobj):
    allowed_ext = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_ext:
        return False
    try:
        Image.open(fileobj).verify()
        fileobj.seek(0)  # Volver al principio para guardar después
        return True
    except Exception:
        return False
