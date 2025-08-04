import os
import os.path

from nickelodeon.models import MP3Song
from nickelodeon.utils import (
    AVAILABLE_FORMATS,
    s3_object_exists,
    s3_upload,
)


def move_file(instance_id, from_filename, to_filename):
    song = None
    try:
        song = MP3Song.objects.get(id=instance_id)
    except MP3Song.DoesNotExist:
        return
    song.filename = from_filename
    try:
        song.move_file_to(to_filename)
    except Exception:
        return
    finally:
        song.save()
    return


def move_files_to_destination(dst_folder, safe_title, extensions, tmp_paths):
    filename = safe_title
    attempt = 0
    while True:
        file_exist = False
        for ext, lib in AVAILABLE_FORMATS.items():
            if attempt == 0:
                filename = "{}.{}".format(safe_title, ext)
            else:
                filename = "{} ({}).{}".format(safe_title, attempt, ext)
            final_path = os.path.join(dst_folder, filename)
            if ext in extensions and s3_object_exists(final_path):
                file_exist = True
                break
        if not file_exist:
            break
        attempt += 1
    for ext, lib in AVAILABLE_FORMATS.items():
        if ext in extensions:
            if attempt == 0:
                filename = safe_title
            else:
                filename = "{} ({})".format(safe_title, attempt)
            final_path = os.path.join(dst_folder, filename + "." + ext)
            with open(tmp_paths[ext], mode="rb") as f:
                s3_upload(f, final_path)
            os.remove(tmp_paths[ext])
    return filename
