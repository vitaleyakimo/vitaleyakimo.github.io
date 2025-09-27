import os
import json
import time
from pathlib import Path

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_multicategory_file(filepath):
    if not os.path.isfile(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()

    result = {}
    current_category = None
    current_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("category="):
            if current_category is not None:
                result[current_category] = current_lines
            current_category = stripped.split("=", 1)[1]
            current_lines = []
        else:
            if stripped:
                current_lines.append(stripped)

    if current_category is not None:
        result[current_category] = current_lines

    return result

def main():
    print("🔄 Обновление portfolio.json из links.txt и info.txt")
    print("Файлы должны лежать в одной папке с portfolio.json\n")

    portfolio_input = input("Путь до portfolio.json (Enter = ./portfolio.json): ").strip()
    if not portfolio_input:
        portfolio_input = "portfolio.json"

    portfolio_path = Path(portfolio_input).resolve()
    if not portfolio_path.is_file():
        print(f"❌ Файл не найден: {portfolio_path}")
        time.sleep(5)
        return

    # Определяем папку, где лежит portfolio.json
    base_dir = portfolio_path.parent
    links_path = base_dir / "links.txt"
    info_path = base_dir / "info.txt"

    print(f"📁 Рабочая папка: {base_dir}")
    print(f"🔍 Ищу: {links_path.name} и {info_path.name}")

    if not links_path.is_file():
        print(f"❌ Не найден: {links_path}")
        time.sleep(5)
        return
    if not info_path.is_file():
        print(f"❌ Не найден: {info_path}")
        time.sleep(5)
        return

    try:
        portfolio = load_json(portfolio_path)
    except Exception as e:
        print(f"❌ Ошибка чтения portfolio.json: {e}")
        time.sleep(5)
        return

    mode = input("Режим:\n1 — Добавить (по умолчанию)\n2 — Перезаписать\nВыбор: ").strip()
    overwrite = (mode == "2")

    links_data = parse_multicategory_file(links_path)
    info_data = parse_multicategory_file(info_path)

    if links_data is None or not links_data:
        print("❌ links.txt пуст или не содержит корректных блоков category=...")
        time.sleep(5)
        return
    if info_data is None or not info_data:
        print("❌ info.txt пуст или не содержит корректных блоков category=...")
        time.sleep(5)
        return

    all_categories = set(links_data.keys()) | set(info_data.keys())
    processed = 0

    for cat in sorted(all_categories):
        links = links_data.get(cat, [])
        info = info_data.get(cat, [])

        if not links or not info:
            print(f"⚠️  Пропущена категория '{cat}': не хватает ссылок или описаний.")
            continue

        if len(links) != len(info):
            n = min(len(links), len(info))
            print(f"⚠️  Несовпадение в '{cat}': {len(links)} ссылок, {len(info)} описаний → используем {n}")
            links, info = links[:n], info[:n]

        new_entries = [{"url": url, "alt": desc} for url, desc in zip(links, info)]

        if cat not in portfolio:
            print(f"🆕 Создаём категорию: {cat}")
            portfolio[cat] = {"photos": new_entries}
        else:
            if overwrite:
                print(f"🔄 Перезапись категории: {cat} ({len(new_entries)} фото)")
                portfolio[cat]["photos"] = new_entries
            else:
                print(f"➕ Добавление в категорию: {cat} (+{len(new_entries)} фото)")
                portfolio[cat]["photos"].extend(new_entries)

        processed += 1

    if processed == 0:
        print("❌ Ни одна категория не была обработана.")
        time.sleep(5)
        return

    try:
        save_json(portfolio_path, portfolio)
        print(f"\n✅ Успешно обновлён: {portfolio_path}")
        print(f"Обработано категорий: {processed}")
    except Exception as e:
        print(f"❌ Ошибка записи: {e}")
        time.sleep(10)
        return

    print("\nЗавершение через 30 секунд...")
    time.sleep(30)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Прервано.")
    except Exception as e:
        print(f"💥 Ошибка: {e}")
        time.sleep(10)