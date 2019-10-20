## IGNORE ##

import urllib.request

fp = urllib.request.urlopen("http://www.python.org")
my_bytes = fp.read()

my_str = my_bytes.decode("utf8")
fp.close()

# print(my_str)

lines = my_str.split("\n")
[print(l) for l in lines]
