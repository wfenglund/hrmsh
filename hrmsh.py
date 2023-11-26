import sys
import os
import cmd
import readline
import re
import subprocess

### Set:
home = "/home/william/"
# ladda fil som läser in färgval etc.

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

def setprompt(home = home):
path = os.getcwd().replace(home, '~/')
if path == home[:-1]:
path = '~/'
path_depth = path.split('/')
if len(path_depth) > 4:
path_middle_new = [i.replace(i, i[0]) for i in path_depth[1:-1]]
path_middle_new = '/'.join(path_middle_new)
path_middle_old = '/'.join(path_depth[1:-1])
path = path.replace(path_middle_old, path_middle_new)
hrmsh.prompt = mkviolet('{hrmsh}') + ' ' + path + mkviolet(' @\" ')

def list_items(path):
dir_list = list(os.scandir(path))
dir_list = [i.name + '/' if i.is_dir() else i.name for i in dir_list]
return(dir_list)

def colorize_output(in_list):
out_list = [mkyellow(i) if i.endswith('/') else i for i in in_list]
out_list = [mkred(i) if i.endswith('.zip') or i.endswith('.gz') else i for i in out_list]
return(out_list)

### Classes:
class hrmsh(cmd.Cmd):
def do_ls(self, line):
line = line.split()
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

dir_list = list_items(path)
dir_list = sorted(dir_list, key = lambda s: s.lower())

if hidden == True:
dir_list = [i for i in dir_list if i.startswith('.') == False]
if listed == True:
dir_list = colorize_output(dir_list)
for item in dir_list:
print(item)
else:
print(dir_list)

def do_cd(self, line, home = home):
if len(line) == 0:
os.chdir(home)
else:
os.chdir(line)
setprompt()

def do_cat(self, line):
line = line.split()
if len(line) == 1:
with open(line[0], 'r') as file:
for line in file:
print(line.strip())

def do_touch(self, line):
pass

def do_cwd(self, line):
print(os.getcwd())

def do_EOF(self, line):
return(True)

def do_q(self, line):
return(True)

def emptyline(self):
pass

def default(self, line):
allowed_commands = ['vim', 'python']
if self.lastcmd.split()[0] in allowed_commands:
try:
subprocess.run(self.lastcmd.split())
except Exception:
print(f'Fail. "{self.lastcmd}" is not a valid or allowed command.')
else:
print(f'Fail. "{self.lastcmd}" is not a valid or allowed command.')

def precmd(self, line):
setprompt()
return line

def completedefault(self, text, line, begidx, endidx):
line_list = line.split()
if len(text) == 0:
if len(line.split()) == 1:
return(list_items('.'))
else:
return(list_items(line.split()[-1]))
elif text == '..':
return(['../'])
else:
if '/' in line_list[-1] or './' in line_list[-1] or '../' in line_list[-1]:
path = re.sub('^(.*?)\/', '/', line_list[-1][::-1])[::-1]
part = line_list[-1].replace(path, '')
dir_list = list_items(path)
return [i for i in dir_list if part in i]
else:
return [i for i in list_items('.') if text in i]

def complete_cd(self, text, line, begidx, endidx):
line_list = line.split()
if len(text) == 0:
if len(line.split()) == 1:
return([i for i in list_items('.') if i.endswith('/')])
else:
return([i for i in list_items(line.split()[-1]) if i.endswith('/')])
elif text == '..':
return(['../'])
else:
if '/' in line_list[-1] or './' in line_list[-1] or '../' in line_list[-1]:
path = re.sub('^(.*?)\/', '/', line_list[-1][::-1])[::-1]
part = line_list[-1].replace(path, '')
dir_list = list_items(path)
return [i for i in dir_list if part in i and i.endswith('/')]
else:
return [i for i in list_items('.') if text in i and i.endswith('/')]

### Main:
setprompt()

# generate methods for character shell:
# for key in chsh_keys:
#     def tmp_func(self, line, dictionary = chsh_dict):
#         command = readline.get_history_item(readline.get_current_history_length())
#         item = command.split(' ')[0]
#         print(f'The value of \033[96m{item}\033[0m is \033[96m{dictionary[item]}\033[0m.')
#     setattr(charshell, 'do_' + key, classmethod(tmp_func))

# start shell-method:
hrmsh().cmdloop()

### issues:
# fix so that folders end with a '/'
# add aliases
# fix 'do_touch()'
