from student import get_students,calculate_result
from ranking import rank_students
from report import display_students

a=get_students()
b=calculate_result(a)
c=rank_students(b)
display_students(c)