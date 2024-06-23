# hrmsh
A simple shell written in python.

## Settings
You can add aliases and functions in a file called `hrmrc.py` in your home directory. These will then be accessible by your hrmsh session.

### Aliases
In order to make an alias, first initiate the alias dictionary:
```python
alias = {}
```
Then add any aliases that you want, like this:
```python
alias['la'] = 'ls -a'
alias['up'] = 'cd ..'
```
