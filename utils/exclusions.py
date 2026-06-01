import fnmatch
import os
import stat


def is_hidden_file(filepath):
    name = os.path.basename(filepath)
    return name.startswith(".")


def is_system_file(filepath):
    try:
        return bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_SYSTEM)
    except (AttributeError, OSError):
        return False


def match_exclusion(filename, patterns):
    for pattern in patterns:
        if fnmatch.fnmatch(filename, pattern):
            return True
    return False


def is_excluded(filepath, config):
    name = os.path.basename(filepath)
    ext = os.path.splitext(name)[1].lower()
    dirname = os.path.dirname(filepath)

    if config.get("exclude_hidden", True) and is_hidden_file(filepath):
        return True, "hidden file"

    if config.get("exclude_system", True) and is_system_file(filepath):
        return True, "system file"

    for excl_dir in config.get("exclude_dirs", []):
        if excl_dir in filepath.split(os.sep):
            return True, f"excluded directory ({excl_dir})"

    if match_exclusion(name, config.get("exclude_extensions", [])):
        return True, f"excluded extension ({ext})"

    max_mb = config.get("max_file_size_mb", 100)
    try:
        if os.path.getsize(filepath) > max_mb * 1024 * 1024:
            return True, f"file too large (>{max_mb}MB)"
    except OSError:
        return True, "cannot access file size"

    return False, ""
