# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os.path
from datetime import datetime

from jsonschema import validate
from jsonschema.exceptions import ValidationError


def validation(instance):
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "surname": {"type": "string"},
                "name": {"type": "string"},
                "zodiac": {"type": "string"},
                "birthday": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minitems": 3,
                },
            },
            "required": ["surname", "name", "birthday"],
        },
    }
    try:
        validate(instance, schema=schema)
        return True
    except ValidationError as err:
        print(err.message)
        return False


def load_people(file_name):
    with open(file_name, "r") as f:
        people = json.load(f)

    if validation(people):
        return people


def save_people(file_name, people_list):
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(people_list, f, ensure_ascii=False, indent=4)


def add_person(people, surname, name, zodiac, birthday):
    people.append(
        {
            "surname": surname,
            "name": name,
            "zodiac": zodiac,
            "birthday": birthday.split("."),
        }
    )
    return people


def display_people(people):
    """
    Отобразить список людей.
    """
    if people:
        line = "+-{}-+-{}-+-{}-+-{}-+-{}-+".format(
            "-" * 4, "-" * 30, "-" * 30, "-" * 20, "-" * 20
        )
        print(line)
        print(
            "| {:^4} | {:^30} | {:^30} | {:^20} | {:^20} |".format(
                "№", "Фамилия", "Имя", "Знак зодиака", "Дата рождения"
            )
        )
        print(line)

        for idx, person in enumerate(people, 1):
            print(
                "| {:>4} | {:<30} | {:<30} | {:<20} | {:>20} |".format(
                    idx,
                    person.get("surname", ""),
                    person.get("name", ""),
                    person.get("zodiac", ""),
                    ".".join(person.get("birthday", "")),
                )
            )
        print(line)
    else:
        print("Список пуст")


def select_people(surname, people):
    """
    Выбрать людей с заданной фамилией.
    """
    result = []
    for i in people:
        if i.get("surname", "") == surname:
            result.append(i)
    return result


def get_instructions():
    print("add - добавление нового человека;")
    print("info - данные о человеке по его фамилии;")
    print("exti - завершение программы;")
    print("list - вывод информации о всех людях;")
    print("load - загрузить данные из файла;")
    print("save - сохранить данные в файл;")


def main(command_line=None):
    """
    Главная функция программы.
    """
    # Создать родительский парсер для определения имени файла.
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "filename", action="store", help="The data file name"
    )

    # Создать основной парсер командной строки.
    parser = argparse.ArgumentParser("people")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    subparsers = parser.add_subparsers(dest="command")

    # Создать субпарсер для добавления человека.
    add = subparsers.add_parser(
        "add", parents=[file_parser], help="Add a new person"
    )
    add.add_argument(
        "-s",
        "--surname",
        action="store",
        required=True,
        help="The person's surname",
    )
    add.add_argument(
        "-n", "--name", action="store", required=True, help="The person's name"
    )
    add.add_argument(
        "-z", "--zodiac", action="store", help="The person's zodiac"
    )
    add.add_argument(
        "-b",
        "--birthday",
        action="store",
        required=True,
        help="The person's birthday",
    )

    # Создать субпарсер для отображения всех людей.
    _ = subparsers.add_parser(
        "display", parents=[file_parser], help="Display people"
    )

    # Создать субпарсер для выбора людей по фамилии.
    select = subparsers.add_parser(
        "select", parents=[file_parser], help="Select people by surname"
    )
    select.add_argument(
        "-s",
        "--surname",
        action="store",
        type=str,
        required=True,
        help="The required surname",
    )

    # Выполнить разбор аргументов командной строки.
    args = parser.parse_args(command_line)

    is_dirty = False
    if os.path.exists(args.filename):
        people = load_people(args.filename)
    else:
        people = []

    match args.command:
        case "add":
            people = add_person(
                people, args.surname, args.name, args.zodiac, args.birthday
            )
            people.sort(
                key=lambda x: datetime.strptime(
                    ".".join(x["birthday"]), "%d.%m.%Y"
                )
            )
            is_dirty = True

        case "select":
            selected = select_people(args.surname, people)
            display_people(selected)

        case "display":
            display_people(people)

    if is_dirty:
        save_people(args.filename, people)


if __name__ == "__main__":
    main()