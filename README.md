# hrmsh
A simple shell written in python.

## Settings
You can add aliases and functions in a file called `hrmrc.py` in your home directory. These will then be accessible by your hrmsh session.

### Aliases
In order to make an alias, first initiate the alias dictionaryi (in `hrmrc.py`):
```python
alias = {}
```
Then add any aliases that you want, like this:
```python
alias['la'] = 'ls -a'
alias['up'] = 'cd ..'
```

### Functions
Functions are not fully functioning (pun intended) in that they can not be piped yet. It i however
possible to do functions where the result does not have to be piped into another application.
Example (in `hrmrc.py`):
```python
def say_hello():
    print("hello")
```
