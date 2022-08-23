#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 Stéphane Caron
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union


@dataclass
class Field:

    """
    A field stores the key path to a value in input dictionaries. The path
    `"foo/bar/blah"` means the value in a dictionary `input` is located at
    `input["foo"]["bar"]["blah"]`.
    """

    label: str
    plot_right: bool = False

    @property
    def keys(self):
        """
        List of keys to search field values from in input data dictionaries.
        """
        return self.label.split("/")


def get_from_keys(
    collection: Union[dict, list], keys: list, default: Optional[Any] = None
):
    """
    Get value `d[key1][key2][...][keyN]` into a dictionary `d` from keys
    `[key1, key2, ..., keyN]`.

    Args:
        collection: Dictionary or list to get value from.
        keys: Sequence of keys to the value.
        default (optional): If provided, return this value if there is nothing
            in `collection` at that field.
    """
    key = keys[0]
    if isinstance(collection, list):
        key = int(key)
    try:
        child = collection[key]
    except KeyError:
        if default is not None:
            return default
        raise
    if len(keys) == 1:
        return child
    try:
        return get_from_keys(child, keys[1:])
    except KeyError as e:
        if default is not None:
            return default
        raise KeyError(f"{key}/{str(e)[1:-1]}")


def get_from_field(
    collection: Union[dict, list], field: str, default: Optional[Any] = None
):
    """
    Get value `d[key1][key2][...][keyN]` into a dictionary `d` from its field
    "key1/key2/.../keyN".

    Args:
        collection: Dictionary or list to get value from.
        field: Field string.
        default (optional): If provided, return this value if there is nothing
            in `collection` at that field.
    """
    keys = field.split("/")
    return get_from_keys(collection, keys, default)


def list_fields(dictionary: dict, prefix: str = "") -> List[str]:
    """
    List all fields available in a given dictionary.

    Args:
        dictionary: Dictionary.

    Returns:
        List of fields in the dictionary.
    """
    fields = []
    for key in dictionary:
        child_prefix = key if not prefix else f"{prefix}/{key}"
        if isinstance(dictionary[key], dict):
            fields.extend(list_fields(dictionary[key], child_prefix))
        else:  # dictionary[key] is a value
            fields.append(child_prefix)
    return fields


def print_fields(dictionary: dict, label: str = "") -> None:
    """
    Print all fields available in a dictionary.

    Args:
        dictionary: Dictionary
        label: Label to identify the dictionary.
    """
    manucure = "\n- "
    fields = list_fields(dictionary)
    print(f"Fields in {label}:" if label else "Fields:", end="")
    print(manucure.join([""] + sorted(fields)))


def set_from_keys(dictionary: dict, keys: list, value) -> None:
    """
    Set the value `d[key1][key2][...][keyN]` into a dictionary `d`.

    Args:
        dictionary: Dictionary to get value from.
        keys: Sequence of keys to the value.
        value: New value.
    """
    key = keys[0]
    if len(keys) > 1:
        if key not in dictionary:
            dictionary[key] = {}
        return set_from_keys(dictionary[key], keys[1:], value)
    dictionary[key] = value


def filter_fields(dictionary: Dict, fields: Optional[List] = None):
    """
    Filter selected fields in a dictionary.

    Args:
        dictionary: Dictionary to filter.
        fields: If given, only print out these selected fields (nested keys in
        "key1/.../keyN" format).

    Returns:
        Filtered dictionary.
    """
    if not fields:
        return dictionary
    output = {}
    for field in fields:
        keys = field.split("/")
        try:
            value = get_from_field(dictionary, field)
            set_from_keys(output, keys, value)
        except KeyError as e:
            print(f"Field {str(e)} not found when looking up '{field}'")
    return output
