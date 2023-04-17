def to_str(x):
    ## converts a number to currency but as a string
    ## return "${:.1f}K".format(x/1000)
    return "${:,.0f}".format(x)

def to_num(x):
    ## converts a dollar string to number
    import regex as re
    from decimal import Decimal
    return Decimal(re.sub(r'[^\d\-.]', '', x))
