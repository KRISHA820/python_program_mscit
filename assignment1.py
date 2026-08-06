a=[1,2,3,4,4,4,5,6,1,6,7,2,8,9,9,9,10]

for i in range(len(a)):
    for j in range(i+1,len(a)):
        if a[i] == a[j]:
            print(a[i])
            break
