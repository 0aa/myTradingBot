from pathlib import Path
from time import time


def get_project_root() -> Path:
    return Path(__file__).parent.parent


def time_it(func):
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        print(f"{func.__name__} took {end_time - start_time} seconds to execute.")
        return result
    return wrapper
