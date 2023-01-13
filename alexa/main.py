from gc import collect, mem_alloc, mem_free
from os import uname

import app

print('\r\n{}'.format(uname()), '\r\nMem Free:', mem_free())

app.start(8080)
