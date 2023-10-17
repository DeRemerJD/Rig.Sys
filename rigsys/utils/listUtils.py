"""A collection of functions that operate on lists."""


def flattenList(targetList):
    """Flatten a list of lists into a single list recursively."""
    flattenedList = []
    for item in targetList:
        if isinstance(item, list):
            flattenedList.extend(flattenList(item))
        else:
            flattenedList.append(item)
    return flattenedList
