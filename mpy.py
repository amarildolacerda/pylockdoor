import os
import machine

print('walking')

for file in os.listdir("src"):
   if '.py' in file:
      f = "./src/"+file
      print(f)

print(os.listdir())

print('end')
