import json
from pathlib import Path

from PySide2.QtCore import *


def read_text_file_to_string(file_path):
    file_to_read = QFile(file_path)
    if file_to_read.exists():
        if file_to_read.open(QFile.ReadOnly):
            return file_to_read.readAll().data().decode('utf-8')
        print(f"Failed to open file at: {file_path}")
        return None


def get_dir_contents(dir_path, *patterns):
    if path_exists(dir_path):
        return [content.as_posix() for pattern in patterns for content in Path(dir_path).glob(f'*{pattern}')]
    return None


def get_sub_dirs(dir_path):
    if path_exists(dir_path):
        return [sub_dir.as_posix() for sub_dir in Path(dir_path).iterdir() if sub_dir.is_dir()]
    return None


def get_dir(file_path):
    if path_exists(file_path):
        return Path(file_path).parent.as_posix()
    return None


def get_basename(path):
    if path_exists(path):
        return Path(path).name
    return None


def get_json_path():
    setting_file_path = Path(get_dir(__file__) + "/settings.json")
    if path_exists(setting_file_path):
        return setting_file_path.as_posix()
    return None


def get_value_from_json(json_file_path, key):
    try:
        with open(json_file_path, 'r') as file:
            json_data = json.load(file)
            value = json_data.get(key)
            return value
    except json.JSONDecodeError as e:
        print(f"Failed to get JSON path: {e}")


def set_root_path(json_file, new_path):
    try:
        with open(json_file, 'r+') as file:
            json_data = json.load(file)
            json_data['asset_path'] = new_path
            json.dumps(json_data)
    except json.JSONDecodeError as e:
        print(f"Failed to update root path: {e}")


def path_exists(path):
    return Path(path).exists()

def clamp(val,min_val,max_val):
    if val <= min_val:
        val = min_val
    if val >= max_val:
        val = max_val
    return val
