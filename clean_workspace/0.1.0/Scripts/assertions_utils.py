
## Comparison between objects

# - compare_strings
# - compare_datetimes
# - compare_is_list_subset


def normalize_string(string: str) -> str:
    """
    Normalizes a string by lowercasing and removing leading/trailling spaces.
    """
    return string.strip().lower()

def compare_strings(
    string1: str,
    string2: str
) -> bool:
    """
    Compares two strings by first lowering case and remove leading/trailling spaces.

    Args:
    string1 (str): The first string to be compared.
    string2 (str): The second string to be compared.

    Returns:
    bool: True if the strings are identical after applying the chosen normalization logic,
            False otherwise.

    Raises:
    TypeError: If any of the arguments is not a string object.
    """

    if not isinstance(string1, str) or not isinstance(string2, str):
        raise TypeError("Both arguments must be string objects.")

    # Remove leading and trailing whitespaces
    string1_processed = normalize_string(string1)
    string2_processed = normalize_string(string2)

    return string1_processed == string2_processed


from datetime import datetime

def compare_datetimes(dt_obj1: datetime, dt_obj2: datetime, comparison_type: str = "eq") -> bool:
    """
    Compares two datetime objects based on a specified comparison type.

    This function allows for flexible comparisons (equality, greater than, less than)
    between two `datetime.datetime` objects. It correctly handles scenarios where
    the original string formats of the datetimes might have varied, as long as
    they were successfully parsed into valid `datetime` objects.

    Args:
        dt_obj1 (datetime.datetime): The first datetime object for comparison.
        dt_obj2 (datetime.datetime): The second datetime object for comparison.
        comparison_type (str): Specifies the type of comparison to perform.
                               Valid options are:
                               - "eq": Checks for exact equality (`dt_obj1 == dt_obj2`).
                               - "gt": Checks if the first datetime is greater than the second (`dt_obj1 > dt_obj2`).
                               - "gte": Checks if the first datetime is greater than or equal to the second (`dt_obj1 >= dt_obj2`).
                               - "lte": Checks if the first datetime is less than or equal to the second (`dt_obj1 <= dt_obj2`).
                               - "lt": Checks if the first datetime is less than the second (`dt_obj1 < dt_obj2`).

    Returns:
        bool: `True` if the comparison condition is met; `False` otherwise.

    Raises:
        TypeError: If either `dt_obj1` or `dt_obj2` is not a `datetime.datetime` object.
        ValueError: If `comparison_type` is not one of the allowed values ("eq", "gt", "lt").
    """
    if not isinstance(dt_obj1, datetime) or not isinstance(dt_obj2, datetime):
        raise TypeError("Both arguments must be datetime objects.")

    if comparison_type == "eq":
        return dt_obj1 == dt_obj2
    elif comparison_type == "gt":
        return dt_obj1 > dt_obj2
    elif comparison_type == "gte":
        return dt_obj1 >= dt_obj2
    elif comparison_type == "lte":
        return dt_obj1 <= dt_obj2
    elif comparison_type == "lt":
        return dt_obj1 < dt_obj2
    else:
        raise ValueError("Invalid comparison type. Must be 'eq', 'gt', 'gte', 'lte', or 'lt'.")

def compare_is_list_subset(search_value, input_list:list, list_comparison_function:str="all") -> bool:
    """
    Checks for the presence of a value or multiple values within a list,
    handling string normalization and flexible list comparisons.

    Args:
        search_value: The item(s) to find. Can be a single value (like a string or int)
                      or a list of values. If it's a string or contains strings,
                      they'll be normalized (e.g., lowercased) for comparison.
        input_list (list): The list to search through. Any strings within this list
                           will also be normalized to ensure consistent comparisons.
        list_comparison_function: Controls how the search behaves when `search_value` is a list.
                                  Must be either "all" or "any":
                                  - "all": Returns `True` only if **every** normalized item
                                           from `search_value` is found in `input_list`.
                                  - "any": Returns `True` if **at least one** normalized item
                                           from `search_value` is found in `input_list`.

    Returns:
        bool: `True` if the search criteria are met; `False` otherwise.

    Raises:
        TypeError: If `input_list` is not actually a list.
        ValueError: If `search_value` is a list and `list_comparison_function`
                    is not set to "all" or "any".
    """

    if not isinstance(input_list, list):
        raise TypeError("input_list must be a list")
    input_list = [normalize_string(item) if isinstance(item, str) else item for item in input_list]


    if isinstance(search_value, str):
        search_value = normalize_string(search_value)
        return search_value in input_list

    elif isinstance(search_value, list):
        if list_comparison_function not in ["all", "any"]:
            raise ValueError("The 'comparison_type' parameter must be 'all' or 'any'.")

        search_value = [normalize_string(item) if isinstance(item, str) else item for item in search_value ]

        if list_comparison_function == "all":
            return all(item in input_list for item in search_value)
        elif list_comparison_function == "any":
            return any(item in input_list for item in search_value)
    else:
        return search_value in input_list
        
    
def compare_is_string_subset(search_value:str, string_to_check:str) -> bool:
    """
    Checks if a search value is a substring of an input string.

    Args:
        search_value (str): The substring to search for.
        string_to_check (str): The string to search within.

    Returns:
        bool: True if the search value is a substring of the input string, False otherwise.
    """
    if not isinstance(string_to_check, str) and not isinstance(search_value, str):
        raise TypeError("string_to_check and search_value must be a list")
    
    # Remove leading and trailing whitespaces
    search_value_processed = normalize_string(search_value)
    string_to_check_processed = normalize_string(string_to_check)

    return search_value_processed in string_to_check_processed
