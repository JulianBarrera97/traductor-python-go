n, k = map(int, input().split())

a = list(map(int, input().split()))
t = list(map(int, input().split()))

base = 0

extra = [0] * n

for i in range(n):
    if t[i] == 1:
        base += a[i]
    else:
        extra[i] = a[i]

window = sum(extra[:k])
best = window

for i in range(k, n):
    window += extra[i]
    window -= extra[i - k]
    best = max(best, window)

print(base + best)