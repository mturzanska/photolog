from os import path

from PIL import Image

from photolog import db, photolog
from photolog.models import Photos


def _save(dest, file_storage, prefix=None):
    filename = file_storage.filename
    if prefix:
        filename = '_'.join(prefix, filename)
    file_storage.save(path.join(dest, filename))


def _get_resized(img_file, width):
    img_copy = img_file.copy()
    img = Image.open(img_copy)
    ratio = width/float(img.size[0])
    height = img.size[1] * ratio
    img.resize((width, height))
    return img


def save_to_album(img_file_storages, album):
    for img in img_file_storages:
        photo = Photos(file_name=img.filename, album_id=album.id)
        album.photos.append(photo)
        db.session.add(photo)
        thumbnail = _get_resized(img, 300)
        large = _get_resized(img, 1920)
        _save(photolog.config['UPLOAD_FOLDER'], thumbnail, prefix='thumb')
        _save(photolog.config['UPLOAD_FOLDER'], large, prefix='large')
