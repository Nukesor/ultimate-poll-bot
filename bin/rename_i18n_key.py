#!/bin/env python3
import os
import argparse
from ruamel.yaml import YAML

yaml = YAML()

parser = argparse.ArgumentParser(
    description="Change an i18n key across all i18n files and the code."
)
parser.add_argument("key", type=str, help="The key to be changed.")
parser.add_argument("target", type=str, help="The new key for the value")
parsed = parser.parse_args()

key = parsed.key
key_splitted = key.split(".")

target = parsed.target
target_splitted = target.split(".")

i18n_files = os.listdir("i18n")
i18n_dicts = {}

for i18n_file in i18n_files:
    with open(f"i18n/{i18n_file}", "r") as handle:
        i18n_dicts[i18n_file] = yaml.load(handle)


def get_and_delete_value(keys, i18n_dict):
    """Get the current value of the dictionary for a given key.

    This also deletes the value from the dictionary, since we want to move it.
    """
    current_dict = i18n_dict
    # Walk to the directory containing the value
    while len(keys) > 1:
        next_key = keys.pop(0)
        if next_key not in current_dict:
            raise Exception(f"Couldn't find key {next_key} in dict {current_dict}")
        current_dict = current_dict[next_key]

    value_key = keys.pop(0)
    # Check if the value exists
    if value_key not in current_dict:
        raise Exception(f"Couldn't find value {value_key} in dict {current_dict}")

    # Get the value and remove the entry from the dictionary
    value = current_dict[value_key]
    del current_dict[value_key]

    return value, i18n_dict


def insert_value(keys, value, i18n_dict):
    """Insert the value at the new key.

    This needs to potentially create new dictionaries and prevent overwriting of existing keys.
    """
    current_dict = i18n_dict
    # Walk to the directory containing the value
    while len(keys) > 0:
        next_key = keys.pop(0)

        # We didn't hit the nested target directory yet
        if len(keys) > 0:
            # Abort if a intermediate key already exists and isn't a dict.
            # This is a conflict and needs to be handled
            if next_key in current_dict and not isinstance(
                current_dict[next_key], dict
            ):
                raise Exception(f"Key {next_key} in dict {current_dict} already exists")

            # Key doesn't exist yet. Create a new dict
            elif next_key not in current_dict:
                current_dict[next_key] = {}

            current_dict = current_dict[next_key]

        else:
            if next_key in current_dict:
                raise Exception(f"Key {next_key} in dict {current_dict} already exists")

            current_dict[next_key] = value

    return i18n_dict


for file_name, i18n_dict in i18n_dicts.items():
    try:
        value, i18n_dict = get_and_delete_value(key_splitted.copy(), i18n_dict)
        i18n_dicts[file_name] = i18n_dict
    except:  # noqa
        print(f"Got exception for language {file_name}")
        continue

    i18n_dict = insert_value(target_splitted.copy(), value, i18n_dict)

    with open(f"i18n/{file_name}", "wb") as handle:
        output = yaml.dump(i18n_dict, handle)

    # os.system(f"yq r --tojson {file_name} | jq . | yq r -")


# Run ruplacer over our code base and replace all key
os.system(f"""ruplacer --go '"{key}"' '"{target}"' """)
