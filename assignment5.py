n=int(input("Enter how many students result to show: "))

students=[]
for i in range(n):
    sroll=input("Enter the student rollnumber: ")
    snm=input("Enter the student name: ")

    sub1=int(input("Enter student python marks: "))
    sub2=int(input("Enter student linux marks: "))
    sub3=int(input("Enter student Dsa marks: "))
    sub4=int(input("Enter student Java marks: "))
    sub5=int(input("Enter student computer Network marks: "))

    total=sub1+sub2+sub3+sub4+sub5
    print("Total= ",total)
    per=total/5
    print("percentage= ",per)

    if per>=90:
        print("A+ Grade")
    elif per>=80:
        print("A Grade")
    elif per>=70:
        print("B+ Grade")
    elif per>=60:
        print("B Grade")
    elif per>=50:
        print("C Grade")
    elif per>=40:
        print("D Grade")
    elif per>=30:
        print("E Grade")
    else:
        "File"
   
    std={"rnm":sroll,
        "nm":snm,
        "python":sub1,
        "linux":sub2,
        "Dsa":sub3,
        "Java":sub4,
        "computer Network":sub5,
        "total":total,
        "percentage":per
      }

    students.append(std)
students.sort(key=lambda x:x["total"],reverse=True)
rank = 1

for i in range(len(students)):

    if i > 0 and students[i]["total"] != students[i - 1]["total"]:
        rank = i + 1

    students[i]["rank"] = rank

for student in students:
    print("\nRoll Number :", student["rnm"])
    print("Name        :", student["nm"])
    print("Total       :", student["total"])
    print("Percentage  :", student["percentage"])
    print("Rank        :", student["rank"])
