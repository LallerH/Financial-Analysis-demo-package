from tkinter import *
from tkinter import font
from tkinter import ttk

def checkbox_selection(canvas: Canvas, workframe: Frame, y_position: int, title: str, fields: dict, keys_order: list, start_italic_from = False):
    '''
    Tkinter checkbox function, with defined fields (arg).
    Arguments:
        canvas: tkinter canvas
        workframe: tkinter frame
        y_position: (int) initial y_position of text
        title: (str) title/subject of the qeury
        fields: (dict) {keys: 'str', values: 'str'}
        keys_order: list, order of key in dict
        start_italic_from /index/: integer / position of fields from font is italic
    Returns:
        str: 'enter' or 'ignore' / which button was pressed
        dict {keys: 'str', values: True/False wheter checkbutton is selected }
    '''
    workframe.update_idletasks()
    frame_width = workframe.winfo_width()
    response = StringVar() 
    vars = {}
    buttons = []

    title_label=Label(workframe, text=title, wraplength=(frame_width-25), fg='red4', bg='azure', justify=LEFT)
    title_label.place(x=0, y=y_position)
    workframe.update_idletasks()
    y_position += (title_label.winfo_height())

    default_font = font.nametofont("TkDefaultFont")
    normal_font = font.Font(family= default_font['family'], size= default_font['size'], weight=default_font['weight'], slant='roman')
    italic_font = font.Font(family= default_font['family'], size= default_font['size'], weight=default_font['weight'], slant='italic')

    for idx,item in enumerate(keys_order):
        vars.update({item:BooleanVar()})
        if start_italic_from == False or idx < (start_italic_from-1): 
            button = Checkbutton(workframe, text=fields[keys_order[idx]], wraplength=(frame_width-25), justify=LEFT,\
                                variable=vars[item], onvalue=1, offvalue=0, bg='azure', activebackground='azure', font=normal_font)
        elif start_italic_from != False and idx >= (start_italic_from-1):
            button = Checkbutton(workframe, text=fields[keys_order[idx]], wraplength=(frame_width-25), justify=LEFT,\
                                variable=vars[item], onvalue=1, offvalue=0, bg='azure', activebackground='azure', font=italic_font)
        buttons.append(button)
        button.place(x = 0, y = y_position)
        workframe.update_idletasks()
        y_position += (button.winfo_height()-5)

    enter_button=Button(workframe, text='Tovább', borderwidth=1, relief=RAISED, activebackground='LightSteelBlue3', activeforeground='red4', bg='LightSteelBlue1', width=6,
                        command=lambda: response.set('enter'))
    enter_button.place(x=0, y=(y_position+13))
    ignore_button=Button(workframe, text='Mégsem', borderwidth=1, relief=RAISED, activebackground='LightSteelBlue3', activeforeground='red4', bg='LightSteelBlue1', width=6,
                        command=lambda: response.set('ignore'))
    ignore_button.place(x=65, y=(y_position+13))
    
    workframe.configure(height=(y_position+82))
    canvas.yview_moveto('1.0')

    enter_button.wait_variable(response)

    for key in vars:
        vars[key] = vars[key].get()
    
    title_label.destroy()
    for item in buttons:
        item.destroy()
    enter_button.destroy()
    ignore_button.destroy()

    return response.get(), vars

def get_user_information_combined(canvas: Canvas, workframe: Frame, y_position: int, title: str, fields: dict, keys_order: list):
    '''
    Tkinter entry and combobox functions, with defined fields (arg).
    Arguments:
        canvas: tkinter canvas
        workframe: tkinter frame
        y_position: (int) initial y_position of text
        title: (str) title/subject of the qeury
        fields: (dict) {keys: 'str', values: list [['str',...], 'str', ['str',...]]}
        keys_order: list, order of key in dict
    Returns:
        str: 'enter' or 'ignore' / which button was pressed
        dict {keys: 'str', values: list [ 'str', 'str', 'str']}
    '''
    workframe.update_idletasks()
    frame_width = workframe.winfo_width()
    response = StringVar() 
    vars = {}
    input_entries = []

    title_label=Label(workframe, text=title, wraplength=(frame_width-25), fg='red4', bg='azure', justify=LEFT)
    title_label.place(x=0, y=y_position)
    workframe.update_idletasks()
    y_position += (title_label.winfo_height())

    for item in keys_order:
        vars.update({item:[StringVar(workframe), StringVar(workframe), StringVar(workframe)]})
        inputentry_left = ttk.Combobox(workframe, textvariable=vars[item][0], width=23, justify=LEFT, state='readonly', values=fields[item][0])
        inputentry_mid = Entry(workframe, textvariable=vars[item][1], borderwidth=2, relief=GROOVE, width=46, justify=LEFT, state=NORMAL)
        inputentry_right = ttk.Combobox(workframe, textvariable=vars[item][2], width=18, justify=LEFT, state='readonly', values=fields[item][2])
        workframe.update_idletasks()
        y_position += 25

        inputentry_left.place(x=0, y=(y_position+3))
        inputentry_mid.place(x=160, y=(y_position+3), height=22)
        inputentry_right.place(x=440, y=(y_position+3))
        inputentry_left.current([0])
        inputentry_right.current([0])

        input_entries.append(inputentry_left)
        input_entries.append(inputentry_mid)
        input_entries.append(inputentry_right)

    input_entries[1].focus_set()

    y_position += 30
    enter_button=Button(workframe, text='Tovább', borderwidth=1, relief=RAISED, activebackground='LightSteelBlue3', activeforeground='red4', bg='LightSteelBlue1', width=6,
                        command=lambda: response.set('enter'))
    enter_button.place(x=0, y=(y_position))
    enter_button['state']=DISABLED
    ignore_button=Button(workframe, text='Mégsem', borderwidth=1, relief=RAISED, activebackground='LightSteelBlue3', activeforeground='red4', bg='LightSteelBlue1', width=6,
                        command=lambda: response.set('ignore'))
    ignore_button.place(x=65, y=(y_position))
    
    def enable_enter_button(*args):
        for keys in vars:
            if vars[keys][1].get():
                enter_button['state']=NORMAL
                break
            else:
                enter_button['state']=DISABLED           
    for key in vars:
        vars[key][1].trace('w', enable_enter_button)

    workframe.configure(height=(y_position+82))
    canvas.yview_moveto('1.0')

    ignore_button.wait_variable(response)

    for key in vars:
        vars[key][0] = vars[key][0].get()
        vars[key][1] = vars[key][1].get()
        vars[key][2] = vars[key][2].get()
    
    title_label.destroy()
    for item in input_entries:
        item.destroy()
    enter_button.destroy()
    ignore_button.destroy()

    return response.get(), vars

def get_user_information_simple(canvas: Canvas, workframe: Frame, y_position: int, title: str, fields: dict, keys_order: list, start_italic_from = False):
    '''
    Tkinter entry functions, with defined fields (arg).
    Arguments:
        canvas: tkinter canvas
        workframe: tkinter frame
        y_position: (int) initial y_position of text
        title: (str) title/subject of the qeury
        fields: (dict) {keys: 'str', values: 'str'}
        keys_order: list, order of key in dict
        start_italic_from /index/: integer / position of fields from font is italic
    Returns:
        str: 'enter' or 'ignore' / which button was pressed
        dict {keys: 'str', values: 'str'}
    '''
    workframe.update_idletasks()
    frame_width = workframe.winfo_width()
    response = StringVar() 
    vars = {}
    input_entries = []

    default_font = font.nametofont("TkDefaultFont")
    normal_font = font.Font(family= default_font['family'], size= default_font['size'], weight=default_font['weight'], slant='roman')
    italic_font = font.Font(family= default_font['family'], size= default_font['size'], weight=default_font['weight'], slant='italic')

    title_label=Label(workframe, text=title, wraplength=(frame_width-25), fg='red4', bg='azure', justify=LEFT)
    title_label.place(x=0, y=y_position)
    workframe.update_idletasks()
    y_position += (title_label.winfo_height())

    for idx,item in enumerate(keys_order):
        if start_italic_from == False or idx < (start_italic_from-1): 
            inputentry = Text(workframe, borderwidth=2, relief=GROOVE, width=98, state=NORMAL, font=normal_font, wrap=WORD)
        elif start_italic_from != False and idx >= (start_italic_from-1):
            inputentry = Text(workframe, borderwidth=2, relief=GROOVE, width=98, state=NORMAL, font=italic_font, wrap=WORD)

        inputentry.insert(INSERT, fields[item])
        vars.update({item: inputentry})

        inputentry.place(x=0, y=y_position, height=66)
        workframe.update_idletasks()
        y_position += (inputentry.winfo_height()+5)
        input_entries.append(inputentry)

    y_position += 10
    enter_button=Button(workframe, text='Tovább', borderwidth=1, relief=RAISED, activebackground='LightSteelBlue3', activeforeground='red4', bg='LightSteelBlue1', width=6,
                        command=lambda: response.set('enter'))
    enter_button.place(x=0, y=(y_position))
    ignore_button=Button(workframe, text='Mégsem', borderwidth=1, relief=RAISED, activebackground='LightSteelBlue3', activeforeground='red4', bg='LightSteelBlue1', width=6,
                        command=lambda: response.set('ignore'))
    ignore_button.place(x=65, y=(y_position))
    
    workframe.configure(height=(y_position+82))
    canvas.yview_moveto('1.0')

    ignore_button.wait_variable(response)

    for key in vars:
        vars[key] = vars[key].get("1.0", "end -1 chars")
    
    title_label.destroy()
    for item in input_entries:
        item.destroy()
    enter_button.destroy()
    ignore_button.destroy()

    return response.get(), vars


if __name__ == '__main__':
    import sys
    
    window = Tk()
    window.geometry('900x600')

    canvas=Canvas(window, bd=0, highlightthickness=0, bg='azure')
    window_width=(window.winfo_width()-2)
    workframe = Frame(canvas, relief=FLAT, width=(window_width-25), height=30, bg='azure', borderwidth=0)
    canvas.create_window((0, 0), window=workframe, anchor="nw")
    canvas.pack(side=LEFT, expand=TRUE, fill=BOTH)
    workframe.pack(side=LEFT, expand=TRUE, fill=BOTH)

    keys_order=['sellingprice_change',
                'inputprice_change',
                'material_structure',
                'new_and_ceased_material']
    
    fields={'sellingprice_change': 'Egy adott termék (egyéb fröccsöntött termékek gyártása) esetében említésre méltó változás történt annak árbevételében. Mindez, a termék esetében alkalmazott, más termékekhez viszonyított árrés függvényében okozhatta az anyagköltséghányad csökkenését.',
            'inputprice_change': 'A meghatározó alapanyag (polietilén granulátum) egységára mérséklődött, amely változás eredményezhette az anyagköltséghányad csökkenését.',
            'material_structure': 'A termelésben felhasznált egyik alapanyag (polipropilén granulátum) igénybe vett mennyisége 5.3%-kal csökkent tárgyvében, amely változás - az alapanyag egyéb anyagokhoz viszonyított árszínvonalának függvényében - eredményezhette az anyagköltséghányad javulását. Megj.: a növekvő mennyiségben felhasznált, esetlegesen olcsóbb anyagok hasonló változást okozhattak a költséghányadban.',
            'new_and_ceased_material': 'A tárgyévben termelésbe került új (PVC), illetve a termelésből kiesett (bakelit) korábbi alapanyag beszerzési ára befolyásolhatta az anyagköltséghányad alakulását.'
    }

    fields_for_getinfo_combined = {'sellingprice_change': [['a','b','c'], '', ['e','f','g']],
                                   'inputprice_change': [['aa','bb','cc'], '', ['ee','ff','gg']],
                                   'material_structure': [['aaa','bbb','ccc'], '', ['eee','fff','gggg', ]],
                                   'new_and_ceased_material': [['aaaa','bbbb','cccc'], '', ['eeee','ffff','gggg']]
    }

    response, vars = checkbox_selection(canvas, workframe, 1, 'Title', fields, keys_order, start_italic_from=2)
    print(response)
    print(vars)

    response, vars = get_user_information_simple(canvas, workframe, 1, 'Indoklás:', fields, keys_order, start_italic_from=2)
    print(response)
    print(vars)

    # response, vars = get_user_information_combined(canvas, workframe, 1, 'Indoklás:', fields_for_getinfo_combined, keys_order)
    # print(response)
    # print(vars)

    print(response)
    print(vars)

    window.mainloop()
    sys.exit