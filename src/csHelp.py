import config as g


def shHelp():
    s = 'versao: jun/20\n'
    s += 'show [config,gpio,mqtt,help]\n'
    s += 'set <var> <n>\n'
    s += 'set model [4-15,clear]\n'
    s += g.events+' <name> [clear,set <n>,trigger <pin>] \n'
    s += 'adc <pin> [get,set <n>]\n'
    s += 'gpio <pin> [get,set <n>,switch]\n'
    s += 'gpio <pin> mode [in/out/adc/pwm]\n'
    s += 'gpio <pin> type <name>\n'
    s += 'gpio <pin> [timeoff/timeon <x>]/[trigger <pin> monostable_NC/bistable_NC] \n'
    s += 'set sleep <n>|sleep <n>\n'
    return s
