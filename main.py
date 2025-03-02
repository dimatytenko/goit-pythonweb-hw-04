import asyncio
import logging
from pathlib import Path
import argparse
import shutil
import os
from typing import List

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def copy_file(source_path: Path, dest_folder: Path) -> None:
    """
    Асинхронно копіює файл у відповідну підпапку на основі розширення
    """
    try:
        # Отримуємо розширення файлу (без крапки)
        extension = source_path.suffix[1:] if source_path.suffix else 'no_extension'

        # Створюємо підпапку для розширення
        extension_folder = dest_folder / extension
        await asyncio.to_thread(extension_folder.mkdir, exist_ok=True)

        # Формуємо шлях призначення
        dest_path = extension_folder / source_path.name

        # Копіюємо файл асинхронно
        await asyncio.to_thread(shutil.copy2, source_path, dest_path)
        logger.info(f'Скопійовано: {source_path} -> {dest_path}')

    except Exception as e:
        logger.error(f'Помилка при копіюванні {source_path}: {str(e)}')


async def read_folder(source_folder: Path, dest_folder: Path) -> None:
    """
    Рекурсивно читає всі файли у вихідній папці та копіює їх
    """
    try:
        tasks: List[asyncio.Task] = []

        # Проходимо по всіх файлах та папках рекурсивно
        for item in source_folder.rglob('*'):
            if item.is_file():
                # Створюємо завдання для копіювання кожного файлу
                task = asyncio.create_task(copy_file(item, dest_folder))
                tasks.append(task)

        # Чекаємо завершення всіх завдань
        if tasks:
            await asyncio.gather(*tasks)

    except Exception as e:
        logger.error(f'Помилка при читанні папки {source_folder}: {str(e)}')


def parse_arguments() -> argparse.Namespace:
    """
    Обробка аргументів командного рядка
    """
    parser = argparse.ArgumentParser(
        description='Асинхронне сортування файлів за розширенням')
    parser.add_argument('source', type=str, help='Шлях до вихідної папки')
    parser.add_argument('destination', type=str,
                        help='Шлях до папки призначення')
    return parser.parse_args()


async def main():
    # Отримуємо аргументи командного рядка
    args = parse_arguments()

    # Перетворюємо шляхи в об'єкти Path
    source_path = Path(args.source)
    dest_path = Path(args.destination)

    # Перевіряємо існування вихідної папки
    if not source_path.exists():
        logger.error(f'Вихідна папка не існує: {source_path}')
        return

    # Створюємо папку призначення, якщо вона не існує
    await asyncio.to_thread(dest_path.mkdir, exist_ok=True)

    # Запускаємо процес сортування
    logger.info('Початок сортування файлів...')
    await read_folder(source_path, dest_path)
    logger.info('Сортування файлів завершено')

if __name__ == '__main__':
    asyncio.run(main())
