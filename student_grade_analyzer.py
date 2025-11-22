import statistics

class Student:
    def __init__(self, name, grades=None):
        self.name = name
        self.grades = grades if grades is not None else []

    def add_grade(self, grade):
        self.grades.append(grade)

    def average(self):
        return sum(self.grades) / len(self.grades) if self.grades else 0

    def highest(self):
        return max(self.grades) if self.grades else None

    def lowest(self):
        return min(self.grades) if self.grades else None

    def median(self):
        return statistics.median(self.grades) if self.grades else None

    def __str__(self):
        return f"{self.name}: {self.grades}"


class GradeAnalyzer:
    def __init__(self):
        self.students = {}

    def add_student(self):
        name = input("Enter student name: ").strip()
        if name in self.students:
            print("Student already exists.")
            return

        self.students[name] = Student(name)
        print(f"Added student: {name}")

    def add_grade_to_student(self):
        name = input("Enter student name: ").strip()
        if name not in self.students:
            print("Student not found.")
            return

        try:
            grade = float(input("Enter grade (0-100): "))
            if grade < 0 or grade > 100:
                raise ValueError
        except ValueError:
            print("Invalid grade.")
            return

        self.students[name].add_grade(grade)
        print(f"Added grade {grade} to {name}")

    def update_student_name(self):
        old_name = input("Enter current name: ").strip()
        if old_name not in self.students:
            print("Student not found.")
            return

        new_name = input("Enter new name: ").strip()
        if new_name in self.students:
            print("Another student already has this name.")
            return

        self.students[new_name] = self.students.pop(old_name)
        self.students[new_name].name = new_name
        print(f"Updated name to {new_name}")

    def remove_student(self):
        name = input("Enter student name to remove: ").strip()
        if name not in self.students:
            print("Student not found.")
            return

        del self.students[name]
        print(f"Removed student {name}")

    def show_student_stats(self):
        name = input("Enter student name: ").strip()
        if name not in self.students:
            print("Student not found.")
            return

        s = self.students[name]
        print(f"\nStatistics for {name}")
        print("-" * 30)
        print(f"Grades: {s.grades}")
        print(f"Average: {s.average():.2f}")
        print(f"Highest: {s.highest()}")
        print(f"Lowest: {s.lowest()}")
        print(f"Median: {s.median()}")
        print("-" * 30)

    def show_all_students(self):
        if not self.students:
            print("No students registered.")
            return

        print("\nAll Students")
        print("-" * 30)
        for name, student in self.students.items():
            print(f"{name}: {student.grades}")
        print("-" * 30)

    def export_report(self):
        filename = "grade_report.txt"
        with open(filename, "w") as f:
            f.write("STUDENT GRADE REPORT\n")
            f.write("====================\n\n")

            for student in self.students.values():
                f.write(f"Name: {student.name}\n")
                f.write(f"Grades: {student.grades}\n")
                f.write(f"Average: {student.average():.2f}\n")
                f.write(f"Highest: {student.highest()}\n")
                f.write(f"Lowest: {student.lowest()}\n")
                f.write(f"Median: {student.median()}\n")
                f.write("-" * 30 + "\n")

        print(f"Report exported to {filename}")
    
    def export_report_csv(self):
        filename = "grade_report.csv"
        with open(filename, "w") as f:
            # Header row
            f.write("name,grade,average,highest,lowest,median\n")

            for student in self.students.values():
                # If the student has no grades, at least one row should still appear
                if not student.grades:
                    f.write(f"{student.name},,,,\n")
                    continue

                # Write one row per grade (useful for ML datasets)
                for g in student.grades:
                    f.write(
                        f"{student.name},"
                        f"{g},"
                        f"{student.average():.2f},"
                        f"{student.highest()},"
                        f"{student.lowest()},"
                        f"{student.median()}\n"
                    )

        print(f"CSV report exported to {filename}")


    def main_menu(self):
        while True:
            print("""
STUDENT GRADE ANALYZER
----------------------
1. Add student
2. Add grade to student
3. Update student name
4. Remove student
5. Show statistics for a student
6. Show all students
7. Export report to file
8. Export report to CSV
9. Exit
""")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                self.add_student()
            elif choice == "2":
                self.add_grade_to_student()
            elif choice == "3":
                self.update_student_name()
            elif choice == "4":
                self.remove_student()
            elif choice == "5":
                self.show_student_stats()
            elif choice == "6":
                self.show_all_students()
            elif choice == "7":
                self.export_report()
            elif choice == "9":
                print("Goodbye!")
                break
            elif choice == "8":
                self.export_report_csv()
            else:
                print("Invalid option. Try again.")


if __name__ == "__main__":
    app = GradeAnalyzer()
    app.main_menu()
