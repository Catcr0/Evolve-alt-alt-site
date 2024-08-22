import json
from os import path
from shutil import copyfile
from sys import argv


def main() -> None:
    """
    Updates the locale-specific strings JSON file based on the default strings JSON file.

    This script compares the default strings in 'strings.json' with the locale-specific strings
    in 'strings.<locale>.json'. It marks new or changed strings with 'TRANS:' or 'CHANGE:' tags
    respectively, and writes the updated strings back to the locale-specific file. It also creates
    a backup of the default strings as 'last-strings.json'.

    Usage:
        python updateString.py <locale>
    """
    if len(argv) < 2:
        print("Please provide the locale key. Usage: python updateString.py <locale>")
        return

    locale = argv[1]

    if not path.exists(f"strings.{locale}.json"):
        print(
            f"File 'strings.{locale}.json' not found. Please create this file with '{{}}' as its content if it doesn't exist."
        )
        return

    try:
        with open("strings.json", encoding="utf-8") as default_file, open(
            f"strings.{locale}.json", "r+", encoding="utf-8"
        ) as loc_file:
            default_strings = json.load(default_file)
            locale_strings = json.load(loc_file)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return

    last_strings = None
    if path.exists("last-strings.json"):
        try:
            with open("last-strings.json", encoding="utf-8") as last_file:
                last_strings = json.load(last_file)
        except json.JSONDecodeError:
            print("The file 'last-strings.json' contains malformed JSON.")

    writing = {}
    trans_count = 0
    change_count = 0

    for key, value in default_strings.items():
        if key in locale_strings:
            if locale_strings[key].startswith("TRANS:"):
                writing[key] = "TRANS:" + value
                trans_count += 1
            elif last_strings and key in last_strings and value != last_strings[key]:
                writing[key] = (
                    f"CHANGE:{locale_strings[key]}~FROM:{last_strings[key]}~TO:{value}"
                )
                change_count += 1
            else:
                writing[key] = locale_strings[key]
            del locale_strings[key]
        else:
            writing[key] = "TRANS:" + value
            trans_count += 1

    print(f"{change_count} values are marked with tag 'CHANGE:'")
    print(f"{trans_count} values are marked with tag 'TRANS:'")
    if locale_strings:
        print(f"{len(locale_strings)} keys were deleted:")
        for key in locale_strings:
            print(key)
    else:
        print("No keys were deleted.")

    with open(f"strings.{locale}.json", "w", encoding="utf-8") as loc_file:
        json.dump(writing, loc_file, ensure_ascii=False, indent=2)

    copyfile("strings.json", "last-strings.json")


if __name__ == "__main__":
    main()
