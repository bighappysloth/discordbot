from pathlib import Path
import argparse
import json
import logging

logger = logging.getLogger(__name__)


# Now Check for Nones.


def getEntryRecursive_dictionary(query, target_dictionary: dict):
    """
    Takes in a string 'p1.p2.p3' and looks for target_dictionary['p1']['p2']['p3']
    Recursively searches a dictionary. Does not perform backup functions like searching in DEFAULT_CONFIG.
    """
    if len(query) == 1 and isinstance(query, list):
        try:
            return {"status": "success", "msg": target_dictionary[query[0]]}
        except KeyError:
            return {"status": "failure", "msg": f'Option "{query[0]}" not found.'}
    else:
        if isinstance(query, str):
            query = query.split(".")  # split by dots if on first execution.
        try:
            if len(query) == 1:
                result = getEntryRecursive_dictionary(query, target_dictionary)
            else:
                result = getEntryRecursive_dictionary(
                    query[1:], target_dictionary[query[0]]
                )
            return result
        except KeyError:
            return {"status": "failure", "msg": f'Option "{query[0]}" not found.'}


if __name__ == "__main__":

    p = (
        Path(".") / r"user_settings" / r"default_settings.json"
    )  # path to default settings.

    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("new_value")

    # Attemping to search through the dictionary
    # args.arg

    try:
        with p.open() as fp:
            j = json.loads(fp.read())
    except FileNotFoundError:
        logger.debug(f"File: {p} not found.")

    logger.debug(
        f"Dictionary: {json.dumps(j,sort_keys=True,indent=4)}, type = {type(j)}"
    )
    args = parser.parse_args()
    logger.debug(f"args: {args}")
    logger.debug(
        f'Finding "{args.input}" recursively: {getEntryRecursive_dictionary(args.input,j)}'
    )
