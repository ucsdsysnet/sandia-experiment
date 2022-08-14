def utf8len(s):
    return len(s.encode('utf-8'))

#numnber of bytes in a string
print(utf8len("memtier-10000000"))
print(utf8len("memtier-0"))