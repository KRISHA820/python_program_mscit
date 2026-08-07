a=input("Enter the paregraph: ")

print(list[a.split(" ")])
b=list(a.split(" "))
print("Total number of words",len(b))
print("Number of unique word",set(b))
print("Longest word",max(b,key=len))
print("shorteat word",min(b,key=len))

for word in b:
    if b.count(word)>1:
        print(word)
