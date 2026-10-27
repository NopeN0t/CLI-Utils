def log(silent : bool, text : str, endl = True) -> None :
    '''Print wrapper that have option to not print'''
    if not silent :
        if endl :
            print(text)
        else :
            print(text, end="")