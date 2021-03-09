import re
import random
import string


def get_random_string(length=32):
    chars = string.ascii_letters + string.digits
    result_str = "".join(random.choice(chars) for _ in range(length))

    return result_str

def generate_secret_values(values):
    creation_values = {}

    for k, v in values.items():
        # the length of the string can be specified by adding the length value in [],
        # e.g. 'gen[64]' for a string with 64 characters
        if re.match(r"^gen\[[0-9]{1,4}\]$", v):
            length = re.search(r"\[([0-9]+)\]", v)
            creation_values[k] = get_random_string(int(length.group(1)))
        elif v == "gen":
            creation_values[k] = get_random_string()
        elif v == "manual":
            raise Exception(f"Value for { k } is set to manual, please create beforehand.")
        else:
            creation_values[k] = v

    return creation_values


def get_change_path(change):
  ret_path = ""
  for c in change:
    ret_path += f".{ c }"
  
  return ret_path
