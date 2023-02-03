
        if (go_sleep > 1):
            if (go_sleep < 2 and g.config['sleep'] > 0):
                mqtt.p(mqtt.tCmdOut()+'/sleep', str(g.config['sleep']))
            go_sleep += 1
            if go_sleep > 60:
                go_sleep = 0
                if (g.config['sleep'] > 0):
                    collect()
                    idle()
                    deepsleep(g.config['sleep'])


def deepsleep(n):
    rtc = RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=DEEPSLEEP)
    if reset_cause() == DEEPSLEEP_RESET:
        print('iniciando deep sleep')
    rtc.alarm(rtc.ALARM0, n*1000)
    #machine.deepsleep()

sv = {"none":None}  
def localTrig(i: str,stype: str,value: int):
    global sv 
    for j in g.config[g.conds]:
        cmd = j.split(',',8)
        c = cmd[2]
        a = int(cmd[3])
        tp = cmd[4] 
        p = cmd[5]
        v = g.strToNum(cmd[6] or str(value))
        if (tp=='s'):
          try: 
            x = sv.get('{}'.format(p)) or '-1'
            if (cmd[0]==stype)  and cmd[1]==i and x != cmd[6]: # and vo != value   :  
                rsp = None
                vo = g.strToNum('{}'.format(value))
                va = g.strToNum('{}'.format(a))
                if (c == 'eq' and vo == va):
                    rsp = 'eq'
                elif (c == 'lt' and vo < va):
                    rsp = 'lt'
                elif (c == 'gt' and vo > va):
                    rsp = 'gt'        
                elif (c == 'ne' and vo != va):
                    rsp = 'ne'

                if (rsp != None):
                    mqtt.p(mqtt.tpfx()+'/scene/'+p,cmd[6])
                    _p = 'scene '+p+' set '+cmd[6]
                    sv['{}'.format(p)] =cmd[6]
                    ev.rcv(_p)
            continue
          except Exception as e: 
                print('error {}, {}=={} and {}=={} {} '.format(cmd,cmd[0],stype,cmd[1],i,e))
        elif (tp=='t'):
            vo = g.strToNum(g.gpin(p))
            if (cmd[0]==stype)  and (cmd[1]==i and (vo != v)):  
                rsp = None;
                if (c=='lt') and (value < a):
                    rsp = g.spin(p, v, True)
                elif (c=='gt') and (value > a):
                    rsp = g.spin(p, v,True)
                elif (c=='eq') and (value == a):
                    rsp = g.spin(p,v, True)
                elif (c=='ne') and (value != a):
                    rsp = g.spin(p,v, True)
                if (rsp != None):
                    mqtt.p(mqtt.tpfx() +'/gpio/' + p, g.gpin(p) )    
            continue   
    collect()
    return 'nok'




    
_N = None
desde = None
def show():
    global desde
    from gc import mem_alloc, mem_free

    import commandutils as u
    desde = desde or u.now()
    from config import IFCONFIG, dados, gKey, uid
    m = ''
    m += ' "time":"%s"' %  u.now()
    m += ' "ssid":"%s"' % gKey('ssid')
    m += ' "alloc":%s' % mem_alloc()
    m += ' "id":"%s"' % uid
    m += ' "ip":"%s"' % dados[IFCONFIG]
    m += ' "free":%s'  % mem_free()
    m += ' "up":"%s"' % desde
    return m
def shMqtt():
    m = ''
    from config import config
    for item in config:
        if ('mqtt' in item):
            m += ' "item":"%s" ' % confg[item]
    return m


        if dt.find(b"/cmd")!=-1:
            from command8266 import cmmd
            cmd = (dt[0:dt.find(b'HTTP/')]).decode('utf-8')
            cmd = (cmd.split('?')[1]).split('=')[1]
            rsp = cmmd(cmd)
            return mkrsp(cli,'{\"result\": %s } ' % rsp,200,'application/json')
