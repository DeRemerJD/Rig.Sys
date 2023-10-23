"""Functions for handling strings."""


def mirrorString(string):
    """Return a mirrored version of the given string.

    If the string starts with "L_" or "R_", it will be mirrored. Otherwise, the string will be returned as-is.

    Args:
        string (str): The string to mirror.

    Returns:
        str: The mirrored string.

    """
    if not isinstance(string, str):
        return string

    leftToken = "L_"
    rightToken = "R_"
    if string.startswith(leftToken):
        string = string.replace(leftToken, rightToken)
    elif string.startswith(rightToken):
        string = string.replace(rightToken, leftToken)

    return string
