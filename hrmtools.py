### External packages:
import os

### Internal packages:
import hrmutils

### Shell functions:
def ls(self, line, stdout = False):
    if type(line) != list:
        line = line.split()
    if type(line) == list and len(line) > 0:
        if type(line[0]) == list:
            line = sum(line, [])
    listed = False
    hidden = True
    if len(line) == 0:
        path = '.'
    elif len(line) < 3:
        if line[0].startswith('-'): # if command contains flags
            if 'l' in line[0]:
                listed = True
            if 'a' in line[0]:
                hidden = False
            if len(line) == 1: # if command only contains flags
                path = '.'
            elif len(line) == 2: # if command also contains path
                path = line[1]
        else:
            path = line[0]
    else:
        print("please supply one argument with or without flags")
        
    dir_list = hrmutils.list_items(path)
    dir_list = sorted(dir_list, key = lambda s: s.lower())

    if hidden == True:
        dir_list = [i for i in dir_list if i.startswith('.') == False]
    if listed == True and stdout == False:
        dir_list = hrmutils.colorize_output(dir_list)
        for item in dir_list:
            print(item)
    elif stdout == False:
        print(dir_list)
    else:
        return dir_list
        
def cat(self, line, stdout = False):
    if type(line) != list:
        line = line.split()
    if type(line[0]) == list:
        line = sum(line, [])
    out_str = ''
    if len(line) == 1:
        with open(line[0], 'r') as file:
            for line in file:
                if stdout == False:
                    print(line.strip())
                out_str = out_str + line
    return out_str

def pwd(self, line):
    print(os.getcwd())
