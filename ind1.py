# !/usr/bin/env python3
# -*- coding: utf-8 -*-

#Для своего варианта лабораторной работы 2.16 необходимо дополнительно реализовать
#интерфейс командной строки (CLI).

import argparse
import json
import sys
from datetime import datetime

from jsonschema import validate
from jsonschema.exceptions import ValidationError


def validation(instance):
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "name1": {"type": "string"},
                "name2": {"type": "string"},
                "number": {"type": "number"},
                },
            },
            "required": ["name1", "name2", "number"],
        }

    try:
        validate(instance, schema=schema)
        return True
    except ValidationError as err:
        print(err.message)
        return False


def help():
    """"
    Функция для вывода списка команд
    """
    # Вывести справку о работе с программой.
    print("Список команд:\n")
    print("add - добавить маршрут;")
    print("list - вывести список маршрутов;")
    print("select <тип> - вывод на экран пунктов маршрута, используя номер маршрута;")
    print("help - отобразить справку;")
    print("exit - завершить работу с программой.")
    print("load - загрузить данные из файла;")
    print("save - сохранить данные в файл;")

def load_point(file_name):
    """Загрузка списка маршрутов из файла."""
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Файл {file_name} не найден.")
    except json.JSONDecodeError as e:
        print(f"Ошибка декодирования JSON в файле {file_name}: {e}")
    except Exception as e:
        print(f"Ошибка при загрузке данных из файла {file_name}: {e}")
    return None



def save_point(file_name, point_list):
    """Сохранение списка маршрутов в файл."""
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(point_list, f, ensure_ascii=False, indent=4)

def add(name1, name2, number):
    """Добавление маршрута в список."""
    return {
        'name1': name1,
        'name2': name2,
        'number': number
    }


def error(command):
    """"
    функция для неопознанных команд
    """
    print(f"Неизвестная команда {command}")


def list(point):
    """"
    Функция для вывода списка добавленных маршрутов
    """
    # Заголовок таблицы.
    line = '+-{}-+-{}-+-{}-+-{}-+'.format(
    '-' * 4,
    '-' * 30,
    '-' * 20,
    '-' * 8
    )
    print(line)
    print(
        '| {:^4} | {:^30} | {:^20} | {:^8} |'.format(
            "№",
            "Начальный пункт.",
            "Конечный пункт",
            "№ маршрута"
        )
    )
    print(line)

    # Вывести данные о всех маршрутах.
    for idx, i in enumerate(point, 1):
        print(
            '| {:>4} | {:<30} | {:<20} | {:>8} |'.format(
                idx,
                i.get('name', ''),
                i.get('name2', ''),
                i.get('number', '')
            )
    )
    print(line)


def select(point):
    """""
    Функция для получения маршрута по его номеру
    """
    # Разбить команду на части для выделения номера маршрута.
    parts = input("Введите значение: ")
    # Проверить сведения работников из списка.

    # Проверить сведения.
    flag = True
    for i in point:
        if i['number'] == int(parts):
            print("Начальный пункт маршрута - ", i["name"])
            print("Конечный пункт маршрута - ", i["name2"])
            flag = False
            break
    if flag:
        print("Маршрут с таким номером не найден")


def parse_args():
    parser = argparse.ArgumentParser(description="Управление маршрутами")
    parser.add_argument('-l', '--load', type=str, help='Загрузить данные из файла')
    parser.add_argument('-s', '--save', type=str, help='Сохранить данные в файл')
    parser.add_argument('-a', '--add', action='store_true', help='Добавить новый маршрут')
    parser.add_argument('-d', '--display', action='store_true', help='Вывести список маршрутов')
    parser.add_argument('-n', '--number', type=int, help='Вывести маршрут по номеру')
    return parser.parse_args()


def main():
    parser = argparse.ArgumentParser(description="Управление маршрутами")
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')

    list_parser = subparsers.add_parser('list', help='Отобразить список маршрутов')
    list_parser.add_argument('filename', type=str, help='Имя файла с маршрутами для отображения')
    add_parser = subparsers.add_parser('add', help='Добавить новый маршрут')
    add_parser.add_argument('filename', type=str, help='Имя файла для сохранения маршрута')
    add_parser.add_argument('-s', '--start', required=True, help='Название начального пункта маршрута', metavar='START')
    add_parser.add_argument('-n', '--end', required=True, help='Название конечного пункта маршрута', metavar='END')
    add_parser.add_argument('-z', '--number', type=int, required=True, help='Номер маршрута', metavar='NUMBER')

    args = parser.parse_args()
    points = load_point(args.filename) if args.command in ['add', 'list', 'select'] else []
    is_dirty = False

    match args.command:

        case 'list':
            if points:
                list(points)
            else:
                print(f"Не удалось загрузить данные из файла {args.filename}.")

        case 'add':
            if args.start and args.end and args.number:
                new_point = add(args.start, args.end, args.number)
                points.append(new_point)
                save_point(args.filename, points)
                print("Маршрут успешно добавлен.")
                is_dirty = True

        case 'select':
            selected_point = select(points, args.number)
            if selected_point:
                print("Выбранный маршрут:")
                print(selected_point)
            else:
                print(f"Маршрут с номером {args.number} не найден.")
                
        case _:
            parser.print_help()
            
    if is_dirty:
        save_point(args.filename, points)

if __name__ == '__main__':
    main()

