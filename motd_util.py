def ordinal(num):
    SUFFIXES = {1: 'st', 2: 'nd', 3: 'rd'}

    if 10 <= num % 100 <= 20:
        suffix = 'th'
    else:
        suffix = SUFFIXES.get(num % 10, 'th')
    return str(num) + suffix