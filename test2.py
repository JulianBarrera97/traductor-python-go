n = int(input())
a = list(map(int, input().split()))

a.sort()

ans = 0
left = 0
for right in range(n):
    while a[right] - a[left] > 5:
        left += 1
    ans = max(ans, right - left + 1)
    
print(ans)