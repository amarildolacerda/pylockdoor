def shGpioP(i):
    try:
        import config as g
        s = ''
        mode = g.gMde(i)
        trigger = g.gTrg(i)
        table = g.gTbl(i)
        timeoff = g.config[g.gpio_timeoff].get(i)
        timeon = g.config[g.gpio_timeon].get(i)
        s = 'gpio '+str(i)+' '
        if mode != None:
            s += g.mdeTs(mode)
        if trigger != None:
            s += ' trigger '+str(trigger)
        if table != None:
            s += ' '+g.tblToStr(table)
        if timeoff != None:
            s += ' timeoff '+str(timeoff)
        if timeon != None:
            s += ' timeon '+str(timeon)
        s += ' value '+str(g.gVlr(i))
    except:
        pass
    return s
def shGpio():
    m = {}
    import config as g
    for i in g.config[g.gp_mde]:
        mode = g.gMde(i)
        if mode != None:
            m[i] = shGpioP(i)
    

    return str(m)