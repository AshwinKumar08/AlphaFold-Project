def sortString(text):    
    a = list(text)
    a.sort()
    b = ""
    for x in a:
        b += x
    return b
