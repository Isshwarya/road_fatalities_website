import inspect
import os


def get_project_dir():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_caller_name(level=1):
    frame = inspect.currentframe()
    for _ in range(level):
        frame = frame.f_back
    return frame.f_code.co_name


def get_all_method_names(cls):
    return [attr for attr in dir(cls) if not attr.startswith("__") and callable(getattr(cls, attr))]


def write_to_file(filepath, content):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as fh:
        fh.write(str(content))
