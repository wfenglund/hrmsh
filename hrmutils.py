import os

### Functions:
def mkcyan(string):
    return("\033[96m" + string + "\033[0m")

def mkyellow(string):
    return("\033[33m" + string + "\033[0m")

def mkred(string):
    return("\033[31m" + string + "\033[0m")

def mkblue(string):
    return("\033[34m" + string + "\033[0m")

def mkviolet(string):
    return("\033[35m" + string + "\033[0m")

def mkvioletbg(string):
    return("\033[0;30;42m" + string + "\033[0m")

def list_items(path):
    dir_list = list(os.scandir(path))
    dir_list = [i.name + '/' if i.is_dir() else i.name for i in dir_list]
    return(dir_list)

def colorize_output(in_list):
    out_list = [mkyellow(i) if i.endswith('/') else i for i in in_list]
    out_list = [mkred(i) if i.endswith('.zip') or i.endswith('.gz') else i for i in out_list]
    return(out_list)
