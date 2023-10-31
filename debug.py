#!/usr/bin/env python3

import collections.abc
import decimal

import pikepdf
from path import Path
from tap import Tap
from ipdb import launch_ipdb_on_exception


class Args(Tap):
    in_pdf: Path  # Input PDF path
    search_term: str  # Search term

    def __init__(self, *args, **kwargs):
        super().__init__(*args, underscores_to_dashes=True, **kwargs)

    def configure(self):
        self.add_argument("-i", "--in_pdf")
        self.add_argument("-s", "--search_term")


def print_mro(obj):
    for cls in obj.__class__.mro():
        print(cls)


def deep_search(obj, substring: str, transform=lambda x: x):
    """
    Deeply searches an object for a substring.
    Supports various collection types using collections.abc.

    Parameters:
        - obj: The object to search.
        - substring: The substring to look for.
        - transform: A function to transform the object if needed.

    Returns:
        A list of paths where the substring was found.
    """
    results = []
    substring = substring.lower()

    # Check if the substring exists in the object itself (for base case)
    def check_substring(o, path):
        # Check if the object is bytes and convert it to string for searching
        if isinstance(o, bytes):
            for encoding in ["utf-8", "utf-16", "utf-32"]:
                try:
                    str_val = o.decode(encoding)
                    if substring in str_val.lower():
                        results.append((path, str_val))
                        break
                except UnicodeDecodeError:
                    continue
        elif isinstance(o, str):
            if substring in o.lower():
                results.append((path, o))

    def _search(obj, path=[]):
        # Apply transformation
        obj = transform(obj)

        # Check the object itself
        check_substring(obj, path)

        # If it's a mapping (like a dictionary)
        if isinstance(obj, collections.abc.Mapping):
            for k, v in obj.items():
                check_substring(k, path + [f"key: {k}"])  # Checking the key
                _search(v, path + [k])  # Recursing on the value

        # If it's an iterable (like list, tuple, set, etc.)
        elif isinstance(obj, collections.abc.Iterable) and not isinstance(obj, (str, bytes, pikepdf.Name)):
            # try:
            for i, item in enumerate(map(transform, obj)):
                _search(item, path + [i])
            # except TypeError:
            #     print(f"failes enumerate on iterable type: {type(obj)} obj: {obj}")

        # If it's any other object, consider its attributes
        elif hasattr(obj, "__dict__"):
            _search(obj.__dict__, path)

    _search(obj)

    return results


# Example usage
class MyClass:
    def __init__(self):
        self.my_attr = "search me"


obj = {
    "name": "Alice",
    "info": {"age": 30, "email": "alice@search.com", "custom": MyClass()},
    "friends": ["Bob", "search this", {"nested": "search deep"}],
    "some_set": {"a", "b", "search in set"},
}

# print(deep_search(obj, "search"))


def xfrm(o):
    if isinstance(o, pikepdf.Name):
        return str(obj)
    elif isinstance(o, pikepdf.Stream):
        return o.unparse(resolved=True)
    elif isinstance(o, pikepdf.Dictionary):
        return dict(o.as_dict())
    elif isinstance(o, pikepdf.String):
        return str(o)
    elif isinstance(o, pikepdf.Array):
        return list(o.as_list())
    elif isinstance(o, decimal.Decimal):
        return str(o)
    return o


def debug(in_path: Path, search_term: str):
    with pikepdf.Pdf.open(in_path, inherit_page_attributes=False) as pdf:
        with launch_ipdb_on_exception():
            for i, o in enumerate(pdf.objects):
                res = deep_search(o, search_term, transform=xfrm)
                if len(res):
                    print(f"obj[{i}] matches: {res}")


def main() -> None:
    args = Args().parse_args()
    debug(args.in_pdf, args.search_term)


if __name__ == "__main__":
    main()
