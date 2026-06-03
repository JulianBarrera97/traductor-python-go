inputs = input().split()
n = int(inputs[0])
t = int(inputs[1])
s = list(input().strip())

for x in range(t):
    i = 0
    while i < n - 1:
        if s[i] == 'B' and s[i + 1] == 'G':
            s[i], s[i + 1] = s[i + 1], s[i]
            i += 2
        else:
            i += 1

aux = ""
print(aux.join(s))