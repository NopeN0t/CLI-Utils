from datetime import timedelta

#Converters
def ConvertTime(start : float, end : float) -> str :
    '''
    Convert time to a humen friendly format
    
    :param time: Hard to read version of time
    :type time: float
    :return: More readable version of time
    :rtype: str
    '''
    return str(timedelta(seconds=round((end - start), 4)))

#User information
def log(silent : bool, text : str, endl = True) -> None :
    '''Print wrapper that have option to not print'''
    if not silent :
        if endl :
            print(text)
        else :
            print(text, end="")
