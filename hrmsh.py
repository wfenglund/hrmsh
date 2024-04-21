### External packages:
import sys
import os
import cmd
import readline
import re
import subprocess

### Internal packages:
import hrmutils # for internal functions
import hrmtools # for shell functions

### Load user settings:
home = os.getenv("HOME") + '/'
if os.path.isfile(home + 'hrmrc.py') == False: # if hrmrc.py does not exist
    open(home + '/hrmrc.py', 'a').close() # create hrmrc.py
sys.path.insert(0, home)
import hrmrc

### Declare dictionaries:
try:
    alias_dict = hrmrc.alias
except AttributeError: # if dictionary does not exist
    alias_dict = {}
variable_dict = {}

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
        return subprocess.Popen(['echo', str(run_cmd(first_cmd, True))], stdout = subprocess.PIPE)
    elif placement == 'middle':
        return subprocess.Popen(['echo', str(run_cmd(first_cmd, True))], stdin = standard_in, stdout = subprocess.PIPE)
    elif placement == 'last':
        return subprocess.check_output(['echo', str(run_cmd(first_cmd, True))], stdin = standard_in)

def read_alias(command):
    cmd_list = command.split('|')
    out_list = []
    for part in cmd_list:
        cmd = part.strip().split(' ')[0].strip()
        if cmd in alias_dict: # check if command is an alias
            alias = alias_dict[cmd]
            part = part.replace(cmd, alias, 1)
        out_list.append(part)
    out_cmd = '|'.join(out_list)
    return out_cmd

def read_variable(command):
    if '\$' in command:
        command = command.replace('\$', '$')
        return command
    elif '$' in command:
        var_calls = re.findall('\$\w+', command)
        for call in var_calls:
            var = call.replace('$', '')
            if var in variable_dict:
                command = command.replace(call, variable_dict[var])
            else:
                return call
        return command
    else:
        return command

def check_tilde(command):
    if '~/' in command:
        command = command.replace('~/', home)
        return command
    else:
        return command

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

### Class:
class hrmsh(cmd.Cmd):
    def do_cd(self, line, home = home):
        if len(line) == 0:
            os.chdir(home)
        else:
            os.chdir(line)
        setprompt()

    def do_EOF(self, line):
        return(True)

    def do_q(self, line):
        return(True)

    def emptyline(self):
        pass

    def default(self, line):
        cmd_list = self.lastcmd.split()
        banned_commands = ['rm', '******']
        if cmd_list[0] not in banned_commands:
            try:
                subprocess.run(cmd_list)
            except Exception:
                print(f'Fail. "{self.lastcmd}" is not a valid or allowed command or variable.')
        elif cmd_list[0] == '******':
            pass
        else:
            print(f'Fail. "{self.lastcmd}" is not a valid or allowed command.')
    
    def precmd(self, line): #before command is run
        setprompt()
        line = check_tilde(line)
        line = read_alias(line)
        line = read_variable(line)
        if '|' in line: #potential bug if pipes are in commands for other reasons
            jamie(line)
            return '******'
        if re.search('^\w+\=".+"$', line.strip()):
            key_dec = line.split('=')[0]
            val_dec = line.split('=')[1].replace('"', '')
            variable_dict[key_dec] = val_dec
            line = '******'
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
        elif text == '__':
            return([home])
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
        elif text == '__':
            return([home])
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

### Load shell functions from module hrmtools:
for func_name in dir(hrmtools):
    if func_name.startswith('__') or func_name in ['os', 'hrmutils']:
        pass
    else:
        func_cur = getattr(globals()['hrmtools'], func_name)
        variables = getattr(func_cur, '__code__').co_varnames
        if variables[0] == 'self' and variables[1] == 'line':
            setattr(hrmsh, "do_" + func_name, classmethod(func_cur))
        else:
            print(hrmutils.mkred(f'Error: Function "{func_name}" not loaded: The first two arguments are not "self" and "line".'))

### Load user functions from module hrmrc:
for func_name in dir(hrmrc):
    if func_name.startswith('__') or func_name in ['os', 'hrmutils', 'alias']:
        pass
    else:
        func_cur = getattr(globals()['hrmrc'], func_name)
        variables = getattr(func_cur, '__code__').co_varnames
        if len(variables) < 2:
            if len(variables) == 1:
                def wrap(self, line): func_cur(line)
            if len(variables) == 0:
                def wrap(self, line): func_cur()
            setattr(hrmsh, "do_" + func_name, classmethod(wrap))
        elif variables[0] == 'self' and variables[1] == 'line':
            setattr(hrmsh, "do_" + func_name, classmethod(func_cur))
        else:
            print(hrmutils.mkred(f'Error: Function "{func_name}" not loaded: The first two arguments are not "self" and "line".'))

### Make user aliases tab completable:
def tmp(): return "nothing"
for key in alias_dict:
    if 'do_' + key not in dir(hrmsh):
        setattr(hrmsh, 'do_' + key, classmethod(tmp))

### Make everything in /bin/ tab completable:
bin_binaries = os.listdir('/bin/')
for binary in bin_binaries:
    if 'do_' + binary not in dir(hrmsh):
        setattr(hrmsh, 'do_' + binary + ' ', classmethod(tmp))

### Start shell:
hrmsh().cmdloop()
