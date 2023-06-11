def read_map():
    ## pd.read_excel('fn.xlsx', sheet_name=0, header=2)
    import pandas as pd
    import sys
    mapfile = 'input_files/map.xlsx'
    print('map file:', mapfile)
    
    map = pd.read_excel(mapfile)
    map['Account'] = map['Account'].str.strip()    # strip leading and trailing white space
    map['AccountNum'] = map.Account.str.extract('(^\d+a|^\d+)') # regular expression: numbers followed by a or just numbers
    
    ## only keep needed columns
    ## map = map[['InOrOut', 'Category', 'GreenSheet', 'Committee', 'SourceOfFunds', 'Account', 'AccountNum']]
    map = map[['InOrOut', 'Category', 'SourceOfFunds', 'Account', 'AccountNum']]
    ## print(map.head())

    # check for non-unique account numbers
    df = map.AccountNum
    dups = df[df.duplicated()]
    print(dups)
    if (len(dups) != 0):
        print('')
        print('FATAL ERROR: Duplicate Account numbers in map.xlsx file')
        print('duplicates:')
        print(dups)
        sys.exit()

    return map, dups
