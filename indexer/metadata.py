import datetime
import mimetypes
import os


def get_file_metadata(filepath):
    try:
        stat_info = os.stat(filepath)
        mime_type, _ = mimetypes.guess_type(filepath)
        return {
            "filename": os.path.basename(filepath),
            "extension": os.path.splitext(filepath)[1].lower(),
            "size": stat_info.st_size,
            "created": datetime.datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
            "modified": datetime.datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "mime_type": mime_type or "application/octet-stream",
            "path": filepath,
            "folder": os.path.dirname(filepath),
        }
    except OSError:
        return {
            "filename": os.path.basename(filepath),
            "extension": os.path.splitext(filepath)[1].lower(),
            "size": 0,
            "created": "",
            "modified": "",
            "mime_type": "",
            "path": filepath,
            "folder": os.path.dirname(filepath),
        }
