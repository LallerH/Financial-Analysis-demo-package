if __name__ == '__main__' or __name__=='language_module':
    from dictionary import words_refer_to_price, words_refer_to_increase, words_refer_to_decrease, interfering_words_at_price_change
else:
    from .dictionary import words_refer_to_price, words_refer_to_increase, words_refer_to_decrease, interfering_words_at_price_change

def check_text(*args,**kwargs):
    '''
    Argument:
        text (str) to be checked
        
        check (kwarg) (str)
        
        check = 'includes_price' -> argument contains / referres to "ár"
            returns True/False
        
        check = 'direction' -> argument refers to incerase or decrease of a figure
            returns "increase" or "decrease" or None
    '''
    text_to_check=(args[0])

    if kwargs['check'] == 'includes_price':
        if 'ár' not in text_to_check:
            return False
        else:
            indexes = []
            for idx, item in enumerate(text_to_check):
                if item == 'á' and text_to_check[idx+1] == 'r':
                    indexes.append(idx)
            count = len(indexes)

            for i in range(count):
                if len(text_to_check) == (indexes[i]+2):
                    text_to_check += ' '
                if indexes[i] == 0 and text_to_check[2] == ' ': # 'ár ...'
                    return True
                elif indexes[i] != 0 and text_to_check[indexes[i]-1] == ' ' and text_to_check[indexes[i]+2] == ' ': # '... ár ...'
                    return True
                elif indexes[i] == 0 or text_to_check[indexes[i]-1] == ' ': # 'ár...' or ' ár...'
                    for item in words_refer_to_price:
                        if item in text_to_check[indexes[i]:].split()[0]:
                            return True
                elif indexes[i] != 0 and text_to_check[indexes[i]-1] != ' ': # '...ár...' or '...ár ...'
                    while text_to_check[indexes[i]] != ' ':
                        indexes[i] -= 1
                    if indexes[i] < 0:
                        indexes[i] = 0
                    print(text_to_check[indexes[i]:].split()[0])
                    for item in words_refer_to_price:
                        if (' ' + item) in (' ' + text_to_check[indexes[i]:].split()[0]):
                            return True
            return False
            
    if kwargs['check'] == 'direction':
        for item in interfering_words_at_price_change:
            if item in text_to_check:
                return None
        for item in words_refer_to_increase:
            if item in text_to_check:
                return 'increase'
        for item in words_refer_to_decrease:
            if item in text_to_check:
                return 'decrease'
        return None

if __name__ == '__main__':
    text = 'a magasabb forgalom áremelkedés eredménye'
    print(check_text(text, check = 'includes_price'))
    print(check_text(text, check = 'direction'))

