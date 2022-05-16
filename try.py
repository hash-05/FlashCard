obj = {'age': 30}
a = []
for i in range(3):
    a[i] = obj
print(a)

a[1]['age'] = 22
print(a)
