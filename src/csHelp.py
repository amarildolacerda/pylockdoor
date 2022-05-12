import config as g


def shHelp():
    # return content of file help.tmpl
    with open('help.tmpl', 'r') as f:
        return f.read()
        