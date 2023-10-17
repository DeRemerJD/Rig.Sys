"""A collection of functions that operate on lists."""


def flattenList(targetList):
    """Flatten a list of lists into a single list."""
    targetList = list(targetList)

    if targetList == []:
        return targetList

    if isinstance(targetList[0], list):
        return flattenList(targetList[0]) + flattenList(targetList[1:])

    return targetList[:1] + flattenList(targetList[1:])
