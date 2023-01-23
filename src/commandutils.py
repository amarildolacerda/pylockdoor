def now():
   import utime
   t = utime.localtime()
   return '{}-{}-{}T{}:{}:{}'.format(t[0],t[1],t[2],t[3],t[4],t[5])

      