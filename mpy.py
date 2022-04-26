import os

print('walking')

for file in os.listdir("workSpace"):
   if '.py' in file:
      f = "./workSpace/"+file
      print(f)

print(os.listdir())

print('end')