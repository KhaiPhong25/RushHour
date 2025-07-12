import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def resource_path(relative_path):
    return os.path.join(BASE_DIR, relative_path)