from Framework import common, stringOperations

text = common.Clipboard.get()
lines = stringOperations.textToLines(text)
occ = stringOperations.countLines(lines)
for x in occ:
    print(x[0], x[1])

