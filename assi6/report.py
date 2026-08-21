def display_students(students):

    print("\n")
    print("*" * 85)
    print("             STUDENT RANKING REPORT")
    print("*" * 85)

    print("Rank\tRoll No\tName\t\tTotal \tPercentage\tGrade")

    print("-" * 85)

    for student in students:

        print(
            student["rank"], "\t",
            student["rnm"], " \t",
            student["nm"], "\t\t",
            student["total"], "\t",
            student["percentage"], "\t\t",
            student["grade"]
        )

    print("=" * 85)