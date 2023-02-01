import uselect
import usocket as socket
from utime import ticks_add, ticks_diff, ticks_ms


class MQTTException(Exception):
    pass

def pid_gen(pid=0):
    while True:
        pid = pid + 1 if pid < 65535 else 1
        yield pid
class MQTTClient:

    def __init__(self, client_id, server, port=0, user=None, password=None, keepalive=0,
                 ssl=False, ssl_params=None, socket_timeout=5, message_timeout=10):
        if port == 0:
            port = 8883 if ssl else 1883
        self.client_id = client_id
        self.sock = None
        self.poller_r = None
        self.poller_w = None
        self.server = server
        self.port = port
        self.ssl = ssl
        self.ssl_params = ssl_params if ssl_params else {}
        self.newpid = pid_gen()
        if not getattr(self, 'cb', None):
            self.cb = None
        if not getattr(self, 'cbstat', None):
            self.cbstat = lambda p, s: None
        self.user = user
        self.pswd = password
        self.keepalive = keepalive
        self.lw_topic = None
        self.lw_msg = None
        self.lw_qos = 0
        self.lw_retain = False
        self.rcv_pids = {}  # PUBACK and SUBACK pids awaiting ACK response

        self.last_ping = ticks_ms()  # Time of the last PING sent
        self.last_cpacket = ticks_ms()  # Time of last Control Packet

        self.socket_timeout = socket_timeout
        self.message_timeout = message_timeout

    def _read(self, n):
        if n < 0:
            raise MQTTException(2)
        msg = b''
        while len(msg) < n:
            try:
                rbytes = self.sock.read(n - len(msg))
            except OSError as e:
                if e.args[0] == 11:     # EAGAIN / EWOULDBLOCK
                    rbytes = None
                else:
                    raise
            except AttributeError:
                raise MQTTException(8)
            if rbytes is None:
                self._sock_timeout(self.poller_r, self.socket_timeout)
                continue
            if rbytes == b'':
                raise MQTTException(1) # Connection closed by host (?)
            else:
                msg += rbytes
        return msg

    def _write(self, bytes_wr, length=-1):
        try:
            self._sock_timeout(self.poller_w, self.socket_timeout)
            out = self.sock.write(bytes_wr, length)
        except AttributeError:
            raise MQTTException(8)
        if length < 0:
            if out != len(bytes_wr):
                raise MQTTException(3)
        else:
            if out != length:
                raise MQTTException(3)
        return out

    def _send_str(self, s):
        assert len(s) < 65536
        self._write(len(s).to_bytes(2, 'big'))
        self._write(s)

    def _recv_len(self):
        n = 0
        sh = 0
        while 1:
            b = self._read(1)[0]
            n |= (b & 0x7f) << sh
            if not b & 0x80:
                return n
            sh += 7

    def _varlen_encode(self, value, buf, offset=0):
        assert value < 268435456  # 2**28, i.e. max. four 7-bit bytes
        while value > 0x7f:
            buf[offset] = (value & 0x7f) | 0x80
            value >>= 7
            offset += 1
        buf[offset] = value
        return offset + 1

    def _sock_timeout(self, poller, socket_timeout):
        if self.sock:
            res = poller.poll(-1 if socket_timeout is None else int(socket_timeout * 1000))
            if res:
                for fd, flag in res:
                    if (not flag & uselect.POLLIN) and (flag & uselect.POLLHUP):
                        raise MQTTException(2 if poller == self.poller_r else 3)
                    if (flag & uselect.POLLERR):
                        raise MQTTException(1)
            else:
                raise MQTTException(30)
        else:
            raise MQTTException(28)

    def set_callback(self, f):
        self.cb = f

    def set_callback_status(self, f):
        self.cbstat = f

    def set_last_will(self, topic, msg, retain=False, qos=0):
        assert 0 <= qos <= 2
        assert topic
        self.lw_topic = topic
        self.lw_msg = msg
        self.lw_qos = qos
        self.lw_retain = retain

    def connect(self, clean_session=True):
        self.disconnect()

        ai = socket.getaddrinfo(self.server, self.port)[0]

        self.sock_raw = socket.socket(ai[0], ai[1], ai[2])
        self.sock_raw.setblocking(False)

        try:
            self.sock_raw.connect(ai[-1])
        except OSError as e:
            import uerrno
            if e.args[0] != uerrno.EINPROGRESS:
                raise

        if self.ssl:
            import ussl
            self.sock_raw.setblocking(True)
            self.sock = ussl.wrap_socket(self.sock_raw, **self.ssl_params)
            self.sock_raw.setblocking(False)
        else:
            self.sock = self.sock_raw

        self.poller_r = uselect.poll()
        self.poller_r.register(self.sock, uselect.POLLERR | uselect.POLLIN | uselect.POLLHUP)
        self.poller_w = uselect.poll()
        self.poller_w.register(self.sock, uselect.POLLOUT)

        premsg = bytearray(b"\x10\0\0\0\0\0")
        msg = bytearray(b"\0\x04MQTT\x04\0\0\0")

        sz = 10 + 2 + len(self.client_id)

        msg[7] = bool(clean_session) << 1
        # Clean session = True, remove current session
        if bool(clean_session):
            self.rcv_pids.clear()
        if self.user is not None:
            sz += 2 + len(self.user)
            msg[7] |= 1 << 7  # User Name Flag
            if self.pswd is not None:
                sz += 2 + len(self.pswd)
                msg[7] |= 1 << 6  # # Password Flag
        if self.keepalive:
            assert self.keepalive < 65536
            msg[8] |= self.keepalive >> 8
            msg[9] |= self.keepalive & 0x00FF
        if self.lw_topic:
            sz += 2 + len(self.lw_topic) + 2 + len(self.lw_msg)
            msg[7] |= 0x4 | (self.lw_qos & 0x1) << 3 | (self.lw_qos & 0x2) << 3
            msg[7] |= self.lw_retain << 5

        plen = self._varlen_encode(sz, premsg, 1)
        self._write(premsg, plen)
        self._write(msg)
        self._send_str(self.client_id)
        if self.lw_topic:
            self._send_str(self.lw_topic)
            self._send_str(self.lw_msg)
        if self.user is not None:
            self._send_str(self.user)
            if self.pswd is not None:
                self._send_str(self.pswd)
        resp = self._read(4)
        if not (resp[0] == 0x20 and resp[1] == 0x02):  # control packet type, Remaining Length == 2
            raise MQTTException(29)
        if resp[3] != 0:
            if 1 <= resp[3] <= 5:
                raise MQTTException(20 + resp[3])
            else:
                raise MQTTException(20, resp[3])
        self.last_cpacket = ticks_ms()
        return resp[2] & 1  # Is existing persistent session of the client from previous interactions.

    def disconnect(self):
        if not self.sock:
            return
        try:
            self._write(b"\xe0\0")
        except (OSError, MQTTException):
            pass
        if self.poller_r:
            self.poller_r.unregister(self.sock)
        if self.poller_w:
            self.poller_w.unregister(self.sock)
        try:
            self.sock.close()
        except OSError:
            pass
        self.poller_r = None
        self.poller_w = None
        self.sock = None

    def ping(self):
        self._write(b"\xc0\0")
        self.last_ping = ticks_ms()

    def publish(self, topic, msg, retain=False, qos=0, dup=False):
        assert qos in (0, 1)
        pkt = bytearray(b"\x30\0\0\0\0")
        pkt[0] |= qos << 1 | retain | int(dup) << 3
        sz = 2 + len(topic) + len(msg)
        if qos > 0:
            sz += 2
        plen = self._varlen_encode(sz, pkt, 1)
        self._write(pkt, plen)
        self._send_str(topic)
        if qos > 0:
            pid = next(self.newpid)
            self._write(pid.to_bytes(2, 'big'))
        self._write(msg)
        if qos > 0:
            self.rcv_pids[pid] = ticks_add(ticks_ms(), self.message_timeout * 1000)
            return pid

    def subscribe(self, topic, qos=0):
        assert qos in (0, 1)
        assert self.cb is not None, "Subscribe callback is not set"
        pkt = bytearray(b"\x82\0\0\0\0\0\0")
        pid = next(self.newpid)
        sz = 2 + 2 + len(topic) + 1
        plen = self._varlen_encode(sz, pkt, 1)
        pkt[plen:plen + 2] = pid.to_bytes(2, 'big')
        self._write(pkt, plen + 2)
        self._send_str(topic)
        self._write(qos.to_bytes(1, "little"))  # maximum QOS value that can be given by the server to the client
        self.rcv_pids[pid] = ticks_add(ticks_ms(), self.message_timeout * 1000)
        return pid

    def _message_timeout(self):
        curr_tick = ticks_ms()
        for pid, timeout in self.rcv_pids.items():
            if ticks_diff(timeout, curr_tick) <= 0:
                self.rcv_pids.pop(pid)
                self.cbstat(pid, 0)

    def check_msg(self):
        if self.sock:
            try:
                res = self.sock.read(1)
                if res is None:
                    # wait forever if no timeout, else wait 1 msec
                    if not self.poller_r.poll(-1 if self.socket_timeout is None else 1):
                        self._message_timeout()
                        return None
                    res = self.sock.read(1)
                    if res is None:
                        self._message_timeout()
                        return None
            except OSError as e:
                # 110: ETIMEDOUT 11: EAGAIN/EWOULDBLOCK
                if e.args[0] == 110 or e.args[0] == 11:
                    self._message_timeout()
                    return None
                else:
                    raise e
        else:
            raise MQTTException(28)

        if res == b'':
            raise MQTTException(1) # Connection closed by host

        if res == b"\xd0":  # PINGRESP
            if self._read(1)[0] != 0:
                MQTTException(-1)
            self.last_cpacket = ticks_ms()
            return

        op = res[0]

        if op == 0x40:  # PUBACK
            sz = self._read(1)
            if sz != b"\x02":
                raise MQTTException(-1)
            rcv_pid = int.from_bytes(self._read(2), 'big')
            if rcv_pid in self.rcv_pids:
                self.last_cpacket = ticks_ms()
                self.rcv_pids.pop(rcv_pid)
                self.cbstat(rcv_pid, 1)
            else:
                self.cbstat(rcv_pid, 2)

        if op == 0x90:  # SUBACK Packet fixed header
            resp = self._read(4)
            if resp[0] != 0x03:
                raise MQTTException(40, resp)
            if resp[3] == 0x80:
                raise MQTTException(44)
            if resp[3] not in (0, 1, 2):
                raise MQTTException(40, resp)
            pid = resp[2] | (resp[1] << 8)
            if pid in self.rcv_pids:
                self.last_cpacket = ticks_ms()
                self.rcv_pids.pop(pid)
                self.cbstat(pid, 1)
            else:
                raise MQTTException(5)

        self._message_timeout()

        if op & 0xf0 != 0x30:  # 3.3 PUBLISH – Publish message
            return op
        sz = self._recv_len()
        topic_len = int.from_bytes(self._read(2), 'big')
        topic = self._read(topic_len)
        sz -= topic_len + 2
        if op & 6:  # QoS level > 0
            pid = int.from_bytes(self._read(2), 'big')
            sz -= 2
        msg = self._read(sz) if sz else b''
        retained = op & 0x01
        dup = op & 0x08
        self.cb(topic, msg, bool(retained), bool(dup))
        self.last_cpacket = ticks_ms()
        if op & 6 == 2:  # QoS==1
            self._write(b"\x40\x02")  # Send PUBACK
            self._write(pid.to_bytes(2, 'big'))
        elif op & 6 == 4:  # QoS==2
            raise NotImplementedError()
        elif op & 6 == 6:  # 3.3.1.2 QoS - Reserved – must not be used
            raise MQTTException(-1)

    def wait_msg(self):
        st_old = self.socket_timeout
        self.socket_timeout = None
        out = self.check_msg()
        self.socket_timeout = st_old
        return out