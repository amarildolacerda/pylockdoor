from gc import mem_free
from os import uname

import app

print('\r\n{}'.format(uname()), '\r\nMem Free:', mem_free())

app.run()
