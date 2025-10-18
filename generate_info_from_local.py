import sys
import os
import time
from pathlib import Path
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from deep_translator import GoogleTranslator

# Загружаем модель один раз (первый запуск — долго)
print("Загружаем модель BLIP для генерации описаний...")
print("(Первый запуск может занять 1–2 минуты)\n")

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def parse_links_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
    result = {}
    current_category = None
    current_urls = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("category="):
            if current_category:
                result[current_category] = current_urls
            current_category = stripped.split("=", 1)[1]
            current_urls = []
        elif stripped:
            current_urls.append(stripped)
    if current_category:
        result[current_category] = current_urls
    return result

def get_local_images(folder: Path):
    supported_ext = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif'}
    return sorted([
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in supported_ext
    ])

def get_input_folder():
    if len(sys.argv) > 1:
        # Запуск с аргументом (перетаскивание папки или файла)
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
        print("Перетащите файл из нужной папки на этот скрипт,")
        print("или введите путь к папке с изображениями и links.txt:")
        user_input = input("Путь: ").strip().strip('"')
        return Path(user_input).resolve()

def main():
    try:
        folder = get_input_folder()
        if folder is None:
            input("Нажмите Enter для выхода...")
            return

        links_path = folder / "links.txt"
        if not links_path.is_file():
            print(f"❌ Не найден файл links.txt в папке:\n{folder}")
            input("Нажмите Enter для выхода...")
            return

        # Читаем ссылки
        links_data = parse_links_file(links_path)
        if not links_data:
            print("❌ Файл links.txt пуст или не содержит блоков category=...")
            input("Нажмите Enter для выхода...")
            return

        # Получаем локальные изображения
        local_images = get_local_images(folder)
        total_urls = sum(len(urls) for urls in links_data.values())

        if len(local_images) != total_urls:
            print(f"⚠️ Несовпадение количества:")
            print(f"  Локальных изображений: {len(local_images)}")
            print(f"  Ссылок в links.txt: {total_urls}")
            print("\nУбедитесь, что:")
            print("- Все изображения лежат в этой папке")
            print("- Порядок в links.txt соответствует алфавитному порядку файлов")
            input("\nНажмите Enter для выхода...")
            return

        # Генерация описаний
        print(f"\n🔍 Найдено {len(local_images)} изображений. Генерация описаний...\n")
        info_data = {}
        img_index = 0
        for category, urls in links_data.items():
            print(f"Категория: {category}")
            descs = []
            for url in urls:
                local_img = local_images[img_index]
                print(f"  {local_img.name} → {url}")
                try:
                    with Image.open(local_img) as img:
                        img = img.convert("RGB")
                        inputs = processor(img, return_tensors="pt")
                        out = model.generate(**inputs, max_new_tokens=20)
                        en_caption = processor.decode(out[0], skip_special_tokens=True)
                        ru_caption = GoogleTranslator(source='en', target='ru').translate(en_caption)
                        descs.append(ru_caption)
                        print(f"    → {ru_caption}")
                except Exception as e:
                    error_msg = f"[SEO: ошибка — {str(e)[:50]}]"
                    print(f"    ❌ {error_msg}")
                    descs.append(error_msg)
                img_index += 1
            info_data[category] = descs

        # Сохраняем info.txt в ту же папку
        info_path = folder / "info.txt"
        with open(info_path, "w", encoding="utf-8") as f:
            for category, descs in info_data.items():
                f.write(f"category={category}\n")
                for desc in descs:
                    f.write(f"{desc}\n")

        print(f"\n✅ Успешно создан файл: {info_path}")
        print("\nТеперь запустите update_portfolio.py и укажите путь к portfolio.json")
        input("\nНажмите Enter для выхода...")

    except KeyboardInterrupt:
        print("\n⚠️ Прервано пользователем.")
        input("Нажмите Enter для выхода...")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()