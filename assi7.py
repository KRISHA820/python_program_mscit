from datetime import datetime

class Course:
    def __init__(self, code, day, start_time, end_time):
        self.code = code
        self.day = day.capitalize()

        self.start_time = self.convert_time(start_time)
        self.end_time = self.convert_time(end_time)

        if self.start_time >= self.end_time:
            raise ValueError("End time must be after start time.")

    def convert_time(self, time):
        try:
            t = datetime.strptime(time, "%H:%M")
            return t.hour * 60 + t.minute
        except ValueError:
            raise ValueError("Invalid time! Enter time in HH:MM format.")

    def __str__(self):
        start = f"{self.start_time // 60:02d}:{self.start_time % 60:02d}"
        end = f"{self.end_time // 60:02d}:{self.end_time % 60:02d}"

        return f"{self.code} | {self.day} | {start}-{end}"

class Student:
    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name
        self.courses = []

    def register_course(self, course):
        self.courses.append(course)

    def detect_conflicts(self):
        conflicts = []

        for i in range(len(self.courses)):
            for j in range(i + 1, len(self.courses)):
                c1 = self.courses[i]
                c2 = self.courses[j]

                if (c1.day == c2.day and
                    c1.start_time < c2.end_time and
                    c2.start_time < c1.end_time):

                    conflicts.append((c1, c2))

        return conflicts

    def __str__(self):
        return (
            f"\nStudent ID: {self.student_id}\n"
            f"Student Name: {self.name}\n"
            f"Total Registered Courses: {len(self.courses)}"
        )

    def display_timetable(self):
        print("\nRegistered Timetable:")

        for course in self.courses:
            print(course)

students = []

try:
    n = int(input("Enter number of students: "))

    if n <= 0:
        raise ValueError("Number of students must be positive.")

    for i in range(n):
        print(f"\n--- Student {i + 1} ---")

        student_id = input("Enter Student ID: ")
        name = input("Enter Student Name: ")

        student = Student(student_id, name)

        number = int(input("Enter number of registered courses: "))

        if number < 0:
            raise ValueError("Number of courses cannot be negative.")

        for j in range(number):
            print(f"\nCourse {j + 1}")

            code = input("Enter Course Code: ")
            day = input("Enter Day (Monday-Sunday): ").capitalize()

            if day not in [
                "Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday", "Saturday", "Sunday"
            ]:
                raise ValueError("Invalid day of the week.")

            start = input("Enter Start Time (HH:MM): ")
            end = input("Enter End Time (HH:MM): ")

            course = Course(code, day, start, end)
            student.register_course(course)

        students.append(student)

    print("\n========== STUDENT REPORT ==========")

    for student in students:
        print(student)

        conflicts = student.detect_conflicts()

        if conflicts:
            print("\nTimetable Conflicts Found:")

            for c1, c2 in conflicts:
                print(f"Conflict: {c1.code} <--> {c2.code}")
                print(f"  {c1}")
                print(f"  {c2}")
        else:
            print("\nNo timetable conflicts found.")
            student.display_timetable()

        print("-" * 40)

except ValueError as e:
    print("\nInput Error:", e)

except Exception as e:
    print("\nUnexpected Error:", e)
