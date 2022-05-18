'''
Short script with a simple use of regex, it simply finds all emails in the given file text,
considering the email syntax. A normal email regex question is
rather dead simple and would match 99% of mails probably, but since

"very.(),:;<>[]\".VERY.\"very@\\ \"very\".unusual"@[IPv6:2001:0db8:85a3:0000:0000:8a2e:0370:7334]

is technically a valid email accorting to: https://en.wikipedia.org/wiki/Email_address#Syntax,
the question had to be a bit more comlicated.

Fun fact is that most emails services won't accept an email like that from what I've tested,
which proofs that they only conider stuff like
[a-zA-Z0-9_]+[a-zA-Z0-9_\.]+@[a-zA-Z0-9]+[a-zA-Z0-9\.]+[a-zA-Z0-9]+
a valid email, which technically is wrong.
'''
import re

file = open("tekst.txt")
text = file.read()
file.close()

pattern = re.compile(r'((?<=[ (){},\.])[a-zA-Z0-9!#$%&\'*+-/=?^_`{|}~.]+|"(\\["\\]|[^"])+")@([a-z]+\.[a-z.]+|com|\[IPv6:[0-9a-fA-F:]+\])')
matches = pattern.finditer(text)

for i in matches:
    print(i.group(0))
