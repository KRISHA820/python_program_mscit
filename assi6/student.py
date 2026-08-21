def get_students():

    n = int(input("Enter how many students result to show: "))

    students = []

    for i in range(n):

        sroll = input("Enter the student rollnumber: ")
        snm = input("Enter the student name: ")

        sub1 = int(input("Enter student python marks: "))
        sub2 = int(input("Enter student linux marks: "))
        sub3 = int(input("Enter student Dsa marks: "))
        sub4 = int(input("Enter student Java marks: "))
        sub5 = int(input("Enter student computer Network marks: "))

        std = {
            "rnm": sroll,
            "nm": snm,
            "python": sub1,
            "linux": sub2,
            "Dsa": sub3,
            "Java": sub4,
            "computernetwork": sub5
        }

        # IMPORTANT: this must be inside the for loop
        students.append(std)

    return students


def calculate_result(students):

    for student in students:

        total = (
            student["python"]
            + student["linux"]
            + student["Dsa"]
            + student["Java"]
            + student["computernetwork"]
        )

        percentage = total / 5

        if percentage >= 90:
            grade = "A+"
        elif percentage >= 80:
            grade = "A"
        elif percentage >= 70:
            grade = "B+"
        elif percentage >= 60:
            grade = "B"
        elif percentage >= 50:
            grade = "C"
        elif percentage >= 40:
            grade = "D"
        elif percentage >= 30:
            grade = "E"
        else:
            grade = "F"

        student["total"] = total
        student["percentage"] = percentage
        student["grade"] = grade

    return students