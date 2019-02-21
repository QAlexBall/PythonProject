l = list([1, 2, 3, 4])
s = set(['a', 'b'])
d = dict({'a': 1, 'b': 2})
m = map(lambda x : x * x , l)
for m1 in m:
    print(m1)

print(l)
print(s)
print(d)