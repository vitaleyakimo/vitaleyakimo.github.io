import sys
import time
import msvcrt  # Только для Windows
from pathlib import Path
from datetime import datetime
from PIL import Image

def wait_or_auto_close(timeout=30):
    """Ждёт нажатия клавиши или закрывается через timeout секунд"""
    print(f"\nℹ️  Окно закроется автоматически через {timeout} секунд.")
    print("Нажмите любую клавишу, чтобы закрыть сейчас...")
    start = time.time()
    while time.time() - start < timeout:
        if msvcrt.kbhit():
            msvcrt.getch()
            return
        time.sleep(0.1)

def process_images(input_folder: Path) -> bool:
    if not input_folder.is_dir():
        print("❌ Указанная папка не существует.")
        return False

    output_path = input_folder / "resize"
    output_path.mkdir(exist_ok=True)

    supported_ext = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif'}
    image_files = sorted([
        f for f in input_folder.iterdir()
        if f.is_file() and f.suffix.lower() in supported_ext
    ])

    if not image_files:
        print("⚠️ В папке не найдено изображений для обработки.")
        return False

    current_date = datetime.now().strftime("%Y-%m-%d")

    for idx, img_path in enumerate(image_files, start=1):
        try:
            with Image.open(img_path) as img:
                if img.mode in ("RGBA", "LA", "P"):
                    img = img.convert("RGBA")
                else:
                    img = img.convert("RGB")

                w, h = img.size
                if max(w, h) > 1200:
                    if w > h:
                        new_w, new_h = 1200, int(1200 * h / w)
                    else:
                        new_w, new_h = int(1200 * w / h), 1200
                    img = img.resize((new_w, new_h), Image.LANCZOS)

                new_name = f"{idx:04d}-{current_date}.webp"
                output_file = output_path / new_name

                # Сохраняем с поддержкой прозрачности
                if img.mode == "RGBA":
                    img.save(output_file, "WEBP", quality=90, lossless=False)
                else:
                    img.save(output_file, "WEBP", quality=90)

                print(f"✅ {img_path.name} → {new_name}")

        except Exception as e:
            print(f"❌ Ошибка обработки {img_path.name}: {e}")
            return False

    print(f"\n✨ Успешно обработано {len(image_files)} изображений.")
    print(f"Результаты сохранены в: {output_path}")
    return True

def get_input_folder():
    if len(sys.argv) > 1:
        # Запуск с аргументом (перетаскивание)
        path_arg = Path(sys.argv[1]).resolve()
        if path_arg.is_file():
            return path_arg.parent
        elif path_arg.is_dir():
            return path_arg
        else:
            print("❌ Некорректный путь, переданный при запуске.")
            return None
    else:
        # Ручной ввод
        print("Перетащите файл из нужной папки на этот EXE,")
        print("или введите путь к папке с изображениями:")
        user_input = input("Путь: ").strip().strip('"')
        return Path(user_input).resolve()

def main():
    try:
        folder = get_input_folder()
        if folder is None:
            input("Нажмите Enter для выхода...")
            return

        success = process_images(folder)

        if success:
            # В ЛЮБОМ случае — если успешно → автозакрытие через 30 сек
            wait_or_auto_close(30)
        else:
            # При ошибке — ждём подтверждения
            input("Нажмите Enter для выхода...")

    except Exception as e:
        print(f"❗ Критическая ошибка: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()