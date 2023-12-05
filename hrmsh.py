### External packages:
import sys
import os
import cmd
import readline
import re
import subprocess

### Internal packages:
import hrmrc # for setting
import hrmutils # for internal functions
#import hrmtools # for shell functions

### Set:
import hrmrc
home = hrmrc.home()

### Shell functions:
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
    hrmsh.prompt = hrmutils.mkviolet('{hrmsh}') + ' ' + path + hrmutils.mkviolet(' @\" ') 

def pipe_method(command, placement = 'first', standard_in = ''): # only first working
    first_cmd = ['do_' + command.pop(0), command]
    run_cmd = getattr(hrmsh, first_cmd.pop(0))
    if placement == 'first':
        return subprocess.Popen(['echo', str(run_cmd('', first_cmd, True))], stdout = subprocess.PIPE)
    elif placement == 'middle':
        return subprocess.Popen(['echo', str(run_cmd('', first_cmd, True))], stdin = standard_in, stdout = subprocess.PIPE)
    elif placement == 'last':
        return subprocess.check_output(['echo', str(run_cmd('', first_cmd, True))], stdin = standard_in)

def jamie(bagpipes):
    pipe_list = [i.strip().split() for i in bagpipes.split('|')]
    first_cmd = pipe_list.pop(0) # remove and save first command
    final_cmd = pipe_list.pop() # remove and save final command
    if 'do_' + first_cmd[0] in dir(hrmsh):
        cmd_res = pipe_method(first_cmd)
    else:
        cmd_res = subprocess.Popen(first_cmd, stdout = subprocess.PIPE) # run first command
    for command in pipe_list:
        if 'do_' + command[0] in dir(hrmsh):
            cmd_res = pipe_method(command, placement = 'middle', standard_in = cmd_res.stdout)
        else:
            cmd_res = subprocess.Popen(command, stdin = cmd_res.stdout, stdout = subprocess.PIPE)
    if 'do_' + final_cmd[0] in dir(hrmsh):
        output = pipe_method(final_cmd, placement = 'last', standard_in = cmd_res.stdout)
    else:
        output = subprocess.check_output(final_cmd, stdin = cmd_res.stdout, universal_newlines = True)
    print(output)
    return output

### Classes:
class hrmsh(cmd.Cmd):
    def do_ls(self, line, stdout = False):
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
        
    def do_cd(self, line, home = home):
        if len(line) == 0:
            os.chdir(home)
        else:
            os.chdir(line)
        setprompt()

    def do_cat(self, line, stdout = False):
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

    def do_cwd(self, line):
        print(os.getcwd())

    def do_EOF(self, line):
        return(True)

    def do_q(self, line):
        return(True)

    def emptyline(self):
        pass

    def default(self, line):
        banned_commands = ['rm', '******']
        if self.lastcmd.split()[0] not in banned_commands:
            try:
                subprocess.run(self.lastcmd.split())
            except Exception:
                print(f'Fail. "{self.lastcmd}" is not a valid or allowed command.')
        elif self.lastcmd.split()[0] == '******':
            pass
        else:
            print(f'Fail. "{self.lastcmd}" is not a valid or allowed command.')
    
    def precmd(self, line):
        setprompt()
        if '|' in line: #potential bug if pipes are in commands for other reasons
            jamie(line)
            return '******'
        return line

    def completedefault(self, text, line, begidx, endidx):
        line_list = line.split()
        if len(text) == 0:
            if len(line.split()) == 1:
                return(hrmutils.list_items('.'))
            else:
                return(hrmutils.list_items(line.split()[-1]))
        elif text == '..':
            return(['../'])
        else:
            if '/' in line_list[-1] or './' in line_list[-1] or '../' in line_list[-1]:
                path = re.sub('^(.*?)\/', '/', line_list[-1][::-1])[::-1]
                part = line_list[-1].replace(path, '')
                dir_list = hrmutils.list_items(path)
                return [i for i in dir_list if part in i]
            else:
                return [i for i in hrmutils.list_items('.') if text in i]

    def complete_cd(self, text, line, begidx, endidx):
        line_list = line.split()
        if len(text) == 0:
            if len(line.split()) == 1:
                return([i for i in hrmutils.list_items('.') if i.endswith('/')])
            else:
                return([i for i in hrmutils.list_items(line.split()[-1]) if i.endswith('/')])
        elif text == '..':
            return(['../'])
        else:
            if '/' in line_list[-1] or './' in line_list[-1] or '../' in line_list[-1]:
                path = re.sub('^(.*?)\/', '/', line_list[-1][::-1])[::-1]
                part = line_list[-1].replace(path, '')
                dir_list = hrmutils.list_items(path)
                return [i for i in dir_list if part in i and i.endswith('/')]
            else:
                return [i for i in hrmutils.list_items('.') if text in i and i.endswith('/')]

### Set initial prompt:
setprompt()

### Load shell functions:
# generate methods for character shell:
# for key in chsh_keys:
#     def tmp_func(self, line, dictionary = chsh_dict):
#         command = readline.get_history_item(readline.get_current_history_length())
#         item = command.split(' ')[0]
#         print(f'The value of \033[96m{item}\033[0m is \033[96m{dictionary[item]}\033[0m.')
#     setattr(charshell, 'do_' + key, classmethod(tmp_func))

### Start shell:
hrmsh().cmdloop()

### Issues:
# update so that all functions can be piped (only ls and cat atm)
# update so that not only the first command in pipe chain can be a method
# add aliases
