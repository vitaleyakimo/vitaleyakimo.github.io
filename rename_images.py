import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS

# Поддержка ожидания нажатия клавиши
try:
    import msvcrt
    IS_WINDOWS = True
except ImportError:
    import select
    import termios
    import tty
    IS_WINDOWS = False

def wait_for_keypress_or_timeout(timeout=30):
    if IS_WINDOWS:
        start = time.time()
        while time.time() - start < timeout:
            if msvcrt.kbhit():
                msvcrt.getch()
                return
            time.sleep(0.05)
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            start = time.time()
            while time.time() - start < timeout:
                if select.select([sys.stdin], [], [], 0.05)[0]:
                    sys.stdin.read(1)
                    return
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def get_exif_creation_date(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if exif_data:  # ← ИСПРАВЛЕНО: было "if exif_"
            for tag, value in exif_data.items():
                if TAGS.get(tag, tag) == "DateTimeOriginal":
                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    return None

def get_file_creation_date(file_path):
    try:
        return datetime.fromtimestamp(os.path.getctime(file_path))
    except Exception:
        return datetime.now()

def main():
    folder_path = input("Введите путь к папке с изображениями: ").strip()
    image_folder = Path(folder_path)

    if not image_folder.is_dir():
        print("Ошибка: путь не является папкой.")
        wait_for_keypress_or_timeout(30)
        return

    supported_ext = {'.nef', '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif', '.webp', '.cr2', '.arw', '.dng'}
    image_files = sorted([
        f for f in image_folder.iterdir()
        if f.is_file() and f.suffix.lower() in supported_ext
    ])

    if not image_files:
        print("Не найдено подходящих изображений.")
        wait_for_keypress_or_timeout(30)
        return

    # Создаём папку Rename ВНУТРИ папки с изображениями
    rename_folder = image_folder / "Rename"
    rename_folder.mkdir(exist_ok=True)

    total = len(image_files)
    for idx, file_path in enumerate(image_files, start=1):
        print(f"Текущий файл ({idx}/{total}): {file_path.name}")

        creation_date = get_exif_creation_date(file_path) or get_file_creation_date(file_path)
        date_str = creation_date.strftime("%y-%m-%d")
        new_name = f"{idx:04d}-{date_str}{file_path.suffix.lower()}"
        new_path = rename_folder / new_name

        shutil.copy2(file_path, new_path)

    print("Готово.")
    wait_for_keypress_or_timeout(30)

if __name__ == "__main__":
    main()