"""A collection of functions that operate on lists."""


def flattenList(targetList):
    """Flatten a list of lists into a single list."""
    newList = []
    for item in targetList:
        if isinstance(item, list):
            newList.extend(item)
        else:
            newList.append(item)
    return newList
