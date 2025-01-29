"""This module implement common utils
"""

from os.path import dirname, join


def get_test_json(slug):
    """
    Args:
        slug (str): base name of file
    Return:
        Read and return content of file
    """
    file_path = join(
        dirname(__file__),
        "..",
        "test-data",
        f"{slug}.json",
    )
    with open(file_path, "r", encoding="UTF-8") as f:
        json_value = f.read()
    print("json_value:::", json_value)
    print("type of json values:", type(json_value))
    return json_value
