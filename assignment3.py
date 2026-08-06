passd = input("Enter your password: ")

sp="!@#$%^&*()_+=*-|/:;<>,.?[]{}"

upper=any(a.isupper() for a in passd)
lower=any(a.islower() for a in passd)
digit=any(a.isdigit() for a in passd)
spp=any(a in sp for a in passd)

repeat=False
for i in range(len(passd)-1):
    if passd[i]==passd[i+1]:
        repeat=True
        break

if upper and lower and digit and spp and not repeat:
    print("password is sucsessfully entered")
    
else:
    print("invalid your password")
    if not upper:
        print("missing upper letters")
    if not lower:
        print("missing lower letters")
    if not digit:
        print("missing number")
    if not spp:
        print("missing special character")
    if repeat:
        print("repeated consecutive characters")
   
