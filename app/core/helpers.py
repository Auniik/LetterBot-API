import hashlib
import os
import sys
import time
import traceback
from datetime import datetime


def is_local_env() -> bool:
    return os.getenv('APP_ENV') == 'local'


def safe_get(obj, key):
    return obj.get(key) if obj else None


def verify_base64_image(base64_content: str) -> bool:
    return base64_content.startswith('data:image/') and ';base64,' in base64_content


def time_within_range(start_at, end_at):
    current_time = time.time()

    if start_at is not None and current_time < start_at:
        return False

    if end_at is not None and current_time > end_at:
        return False

    return True


def generate_hash(text):
    # Encode the text to bytes
    text_bytes = text.encode('utf-8')

    # Generate a SHA-256 hash of the text
    hash_object = hashlib.sha256(text_bytes)

    # Convert the hash to a hexadecimal string
    hash_hex = hash_object.hexdigest()

    return hash_hex


def serialize_row(row):
    return {
        k: (v.isoformat() if isinstance(v, datetime) else v)
        for k, v in row.items()
    }


def safe_exception_message(e: Exception, verbose: bool = False) -> str:
    SKIP_FUNCTIONS = {
        "api_call", "load_mocks"
    }
    if verbose:
        return traceback.format_exc()

    exc_type, exc_value, tb = sys.exc_info()
    stack_summary = traceback.extract_tb(tb)
    if not stack_summary:
        return str(e) or e.__class__.__name__

    project_root = os.getcwd()
    last_call = stack_summary[-1]

    if last_call.name in SKIP_FUNCTIONS and len(stack_summary) > 1:
        last_call = stack_summary[-2]

    app_frame = next(
        (frame for frame in reversed(stack_summary)
         if "site-packages" not in frame.filename and "venv" not in frame.filename),
        last_call
    )

    def format_frame(frame):
        rel_path = os.path.relpath(frame.filename, start=project_root)
        return f"{rel_path}@{frame.name}:{frame.lineno}"

    error_class = e.__class__.__name__
    msg = str(e) or error_class

    return (
            f"❌ {error_class}({msg}) | "
            f"{format_frame(last_call)}"
            + (f" ← {format_frame(app_frame)}" if app_frame != last_call else "")
    )
