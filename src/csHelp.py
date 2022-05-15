import config as g
def shHelp():
    readLines('help.tmpl')
def readLines(nome:str):
    with open(nome, 'r') as f:
        return f.readlines()
