from config import gpin, model, sMde, spin, sstype, sTimeOff, sTimeOn, sTrg, swt


def cmd(p, r):
    cmd1 = p[1]
    cmd2 = p[2]
    if cmd1 == "clear":
        return r(model("clear"))
    elif cmd2 == "timeoff":
        return r(sTimeOff(p))
    elif cmd2 == "timeon":
        return r(sTimeOn(p))
    elif cmd2 == "type":
        return r(sstype(cmd1, p[3]))
    else:
        if cmd2 == "set":
            return r(spin(cmd1, p[3]))
        elif cmd2 == "switch":
            return r(swt(cmd1))
        else:
            if cmd2 == "get":
                return r(gpin(p[1]))
            elif cmd2 == "mode":
                return r(sMde(cmd1, p[3]))
            elif cmd2 == "trigger":
                return r(sTrg(p))
    return "Invalido {}".format(p)
