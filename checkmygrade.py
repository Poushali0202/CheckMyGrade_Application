# CheckMyGrade console based Application 
# DATA 200 Lab 1 Project 

import csv
import os
import time
import unittest
from typing import List, Tuple, Optional, Dict, Any
import hashlib
import secrets

# ============================================================================
# PART 1: DATA STRUCTURES
# ============================================================================

class Node:
    def __init__(self, data):
        self.data = data
        self.next: Optional["Node"] = None


class LinkedList:
    def __init__(self):
        self.head: Optional[Node] = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        cur = self.head
        while cur.next:
            cur = cur.next
        cur.next = new_node

    def to_list(self) -> List[Any]:
        out, cur = [], self.head
        while cur:
            out.append(cur.data)
            cur = cur.next
        return out


# ============================================================================
# PART 2: SECURITY & LOGIN
# ============================================================================

class SecurityManager:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = secrets.token_hex(32)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${pwd_hash.hex()}"

    @staticmethod
    def verify_password(stored_hash: str, provided_password: str) -> bool:
        try:
            salt, pwd_hash = stored_hash.split('$')
            provided = hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt.encode(), 100000).hex()
            return provided == pwd_hash
        except Exception:
            return False


class LoginUser:
    def __init__(self, user_id: str, password_hash: str, role: str = "user"):
        self.user_id = user_id
        self.password = password_hash
        self.role = role
        self.is_logged_in = False

    def login(self, provided_password: str) -> bool:
        ok = SecurityManager.verify_password(self.password, provided_password)
        self.is_logged_in = ok
        return ok

    def change_password(self, old_password: str, new_password: str) -> bool:
        if SecurityManager.verify_password(self.password, old_password):
            self.password = SecurityManager.hash_password(new_password)
            return True
        return False


# ============================================================================
# PART 3: DOMAIN CLASSES
# ============================================================================

class Grade:
    def __init__(self, grade_id: str, grade: str, marks_range: str):
        self.grade_id = grade_id
        self.grade = grade
        self.marks_range = marks_range

    def display_grade_report(self) -> str:
        return f"Grade: {self.grade}, Range: {self.marks_range}"


class Course:
    def __init__(self, course_id: str, course_name: str, description: str, credits: int = 3):
        if not course_id or not course_name:
            raise ValueError("Course ID and Name cannot be empty")
        self.course_id = course_id
        self.course_name = course_name
        self.description = description
        self.credits = credits

    def display_courses(self) -> str:
        return f"[{self.course_id}] {self.course_name} - {self.description} (Credits: {self.credits})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Course_id": self.course_id,
            "Course_name": self.course_name,
            "Description": self.description,
            "Credits": self.credits,
        }


class Professor:
    def __init__(self, professor_id: str, name: str, email: str, rank: str, course_id: str):
        if not professor_id or not name or not email:
            raise ValueError("Professor ID, Name, and Email cannot be empty")
        self.professor_id = professor_id
        self.name = name
        self.email = email
        self.rank = rank
        self.course_id = course_id

    def professors_details(self) -> str:
        return f"{self.name} ({self.rank}) - {self.email} - Teaches: {self.course_id}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Professor_id": self.professor_id,
            "Professor_name": self.name,
            "Email": self.email,
            "Rank": self.rank,
            "Course_id": self.course_id,
        }


class Student:
    def __init__(
        self,
        student_id: str,
        first_name: str,
        last_name: str,
        email: str,
        course_id: str,
        grade: str = "N/A",
        marks: float = 0.0,
    ):
        if not student_id or not first_name or not email:
            raise ValueError("Student ID, Name, and Email cannot be empty")
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.course_id = course_id
        self.grade = grade
        self.marks = marks

    def display_records(self) -> str:
        return (
            f"ID: {self.student_id} | {self.first_name} {self.last_name} | "
            f"Email: {self.email} | Course: {self.course_id} | Grade: {self.grade} | Marks: {self.marks}"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Student_id": self.student_id,
            "First_name": self.first_name,
            "Last_name": self.last_name,
            "Email_address": self.email,
            "Course_id": self.course_id,
            "Grade": self.grade,
            "Marks": self.marks,
        }


# ============================================================================
# PART 4: FILE MANAGER
# ============================================================================

class FileManager:
    def __init__(self, folder: str = "data"):
        self.folder = folder
        if not os.path.exists(folder):
            os.makedirs(folder)
        self.student_file = os.path.join(folder, "students.csv")
        self.course_file = os.path.join(folder, "courses.csv")
        self.professor_file = os.path.join(folder, "professors.csv")
        self.login_file = os.path.join(folder, "login.csv")
        self._initialize_files()

    def _initialize_files(self):
        def ensure(path: str, fields: List[str]):
            if not os.path.exists(path):
                with open(path, "w", newline="") as f:
                    w = csv.DictWriter(f, fieldnames=fields)
                    w.writeheader()

        ensure(self.student_file, ["Student_id", "First_name", "Last_name", "Email_address", "Course_id", "Grade", "Marks"])
        ensure(self.course_file, ["Course_id", "Course_name", "Description", "Credits"])
        ensure(self.professor_file, ["Professor_id", "Professor_name", "Email", "Rank", "Course_id"])
        ensure(self.login_file, ["User_id", "Password", "Role"])

    def _read_csv(self, path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(path):
            return []
        with open(path, "r", newline="") as f:
            return list(csv.DictReader(f))

    def _write_csv(self, path: str, rows: List[Dict[str, Any]], fields: List[str]):
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    # Students
    def save_student(self, s: Student):
        rows = [r for r in self._read_csv(self.student_file) if r["Student_id"] != s.student_id]
        rows.append(s.to_dict())
        self._write_csv(self.student_file, rows, ["Student_id", "First_name", "Last_name", "Email_address", "Course_id", "Grade", "Marks"])

    def delete_new_student(self, student_id: str) -> bool:
        rows = self._read_csv(self.student_file)
        new_rows = [r for r in rows if r["Student_id"] != student_id]
        if len(new_rows) != len(rows):
            self._write_csv(self.student_file, new_rows, ["Student_id", "First_name", "Last_name", "Email_address", "Course_id", "Grade", "Marks"])
            return True
        return False

    def load_students(self) -> List[Student]:
        out = []
        for r in self._read_csv(self.student_file):
            try:
                out.append(Student(r["Student_id"], r["First_name"], r["Last_name"], r["Email_address"], r["Course_id"], r["Grade"], float(r["Marks"])))
            except Exception:
                continue
        return out

    # Courses
    def save_course(self, c: Course):
        rows = [r for r in self._read_csv(self.course_file) if r["Course_id"] != c.course_id]
        rows.append(c.to_dict())
        self._write_csv(self.course_file, rows, ["Course_id", "Course_name", "Description", "Credits"])

    def delete_new_course(self, course_id: str) -> bool:
        rows = self._read_csv(self.course_file)
        new_rows = [r for r in rows if r["Course_id"] != course_id]
        if len(new_rows) != len(rows):
            self._write_csv(self.course_file, new_rows, ["Course_id", "Course_name", "Description", "Credits"])
            return True
        return False

    def load_courses(self) -> List[Course]:
        out = []
        for r in self._read_csv(self.course_file):
            try:
                out.append(Course(r["Course_id"], r["Course_name"], r["Description"], int(r.get("Credits", 3))))
            except Exception:
                continue
        return out

    # Professors
    def save_professor(self, p: Professor):
        rows = [r for r in self._read_csv(self.professor_file) if r["Professor_id"] != p.professor_id]
        rows.append(p.to_dict())
        self._write_csv(self.professor_file, rows, ["Professor_id", "Professor_name", "Email", "Rank", "Course_id"])

    def delete_professor(self, professor_id: str) -> bool:
        rows = self._read_csv(self.professor_file)
        new_rows = [r for r in rows if r["Professor_id"] != professor_id]
        if len(new_rows) != len(rows):
            self._write_csv(self.professor_file, new_rows, ["Professor_id", "Professor_name", "Email", "Rank", "Course_id"])
            return True
        return False

    def load_professors(self) -> List[Professor]:
        out = []
        for r in self._read_csv(self.professor_file):
            try:
                out.append(Professor(r["Professor_id"], r["Professor_name"], r["Email"], r["Rank"], r["Course_id"]))
            except Exception:
                continue
        return out

    # Login
    def register_user(self, user_id: str, raw_password: str, role: str = "user"):
        rows = [r for r in self._read_csv(self.login_file) if r["User_id"] != user_id]
        rows.append({"User_id": user_id, "Password": SecurityManager.hash_password(raw_password), "Role": role})
        self._write_csv(self.login_file, rows, ["User_id", "Password", "Role"])

    def load_user(self, user_id: str) -> Optional[LoginUser]:
        for r in self._read_csv(self.login_file):
            if r["User_id"] == user_id:
                return LoginUser(r["User_id"], r["Password"], r.get("Role", "user"))
        return None

    def update_user(self, user: LoginUser):
        rows = [r for r in self._read_csv(self.login_file) if r["User_id"] != user.user_id]
        rows.append({"User_id": user.user_id, "Password": user.password, "Role": user.role})
        self._write_csv(self.login_file, rows, ["User_id", "Password", "Role"])


# ============================================================================
# PART 5: MAIN APPLICATION LOGIC
# ============================================================================

class CheckMyGrade:
    def __init__(self, data_folder: str = "data"):
        self.fm = FileManager(data_folder)
        self.students: List[Student] = self.fm.load_students()
        self.courses: List[Course] = self.fm.load_courses()
        self.professors: List[Professor] = self.fm.load_professors()

    # ---- Student operations
    def add_new_student(self, s: Student) -> bool:
        if any(x.student_id == s.student_id for x in self.students):
            return False
        self.students.append(s)
        self.fm.save_student(s)
        return True

    def update_student_record(self, student_id: str, **kwargs) -> bool:
        for s in self.students:
            if s.student_id == student_id:
                for k, v in kwargs.items():
                    if hasattr(s, k):
                        setattr(s, k, v)
                self.fm.save_student(s)
                return True
        return False

    def delete_new_student(self, student_id: str) -> bool:
        before = len(self.students)
        self.students = [s for s in self.students if s.student_id != student_id]
        removed = self.fm.delete_new_student(student_id)
        return removed or len(self.students) < before

    def search_student(self, field: str, value: Any) -> Tuple[List[Student], float]:
        start = time.time()
        res = [s for s in self.students if getattr(s, field, None) == value]
        elapsed = time.time() - start
        return res, elapsed

    def sort_students(self, field: str, descending: bool = False) -> Tuple[List[Student], float]:
        start = time.time()
        sorted_list = sorted(self.students, key=lambda s: getattr(s, field, ""), reverse=descending)
        elapsed = time.time() - start
        return sorted_list, elapsed

    def get_student_stats(self, course_id: str) -> Dict[str, float]:
        marks = [s.marks for s in self.students if s.course_id == course_id]
        if not marks:
            return {}
        marks.sort()
        n = len(marks)
        avg = sum(marks) / n
        if n % 2:
            med = marks[n // 2]
        else:
            med = (marks[n // 2 - 1] + marks[n // 2]) / 2
        return {"average": avg, "median": med, "min": min(marks), "max": max(marks), "count": n}

    # ---- Course operations
    def add_new_course(self, c: Course) -> bool:
        if any(x.course_id == c.course_id for x in self.courses):
            return False
        self.courses.append(c)
        self.fm.save_course(c)
        return True

    def update_course(self, course_id: str, **kwargs) -> bool:
        for c in self.courses:
            if c.course_id == course_id:
                for k, v in kwargs.items():
                    if hasattr(c, k):
                        setattr(c, k, v)
                self.fm.save_course(c)
                return True
        return False

    def delete_new_course(self, course_id: str) -> bool:
        before = len(self.courses)
        self.courses = [c for c in self.courses if c.course_id != course_id]
        removed = self.fm.delete_new_course(course_id)
        return removed or len(self.courses) < before

    # ---- Professor operations
    def add_new_professor(self, p: Professor) -> bool:
        if any(x.professor_id == p.professor_id for x in self.professors):
            return False
        self.professors.append(p)
        self.fm.save_professor(p)
        return True

    def modify_professor_details(self, professor_id: str, **kwargs) -> bool:
        for p in self.professors:
            if p.professor_id == professor_id:
                for k, v in kwargs.items():
                    if hasattr(p, k):
                        setattr(p, k, v)
                self.fm.save_professor(p)
                return True
        return False

    def delete_professor(self, professor_id: str) -> bool:
        before = len(self.professors)
        self.professors = [p for p in self.professors if p.professor_id != professor_id]
        removed = self.fm.delete_professor(professor_id)
        return removed or len(self.professors) < before

    # ---- Reports
    def generate_student_report(self, student_id: str) -> str:
        s = next((x for x in self.students if x.student_id == student_id), None)
        return s.display_records() if s else "Student not found"

    def generate_course_report(self, course_id: str) -> str:
        enrolled = [s for s in self.students if s.course_id == course_id]
        stats = self.get_student_stats(course_id)
        rep = f"\n=== Course Report: {course_id} ===\n"
        rep += f"Total Students: {len(enrolled)}\n"
        if stats:
            rep += f"Average: {stats['average']:.2f}, Median: {stats['median']:.2f}\n"
            rep += f"Min: {stats['min']:.2f}, Max: {stats['max']:.2f}\n"
        if enrolled:
            rep += "\nStudents:\n" + "\n".join(s.display_records() for s in enrolled)
        return rep

    def generate_professor_report(self, professor_id: str) -> str:
        p = next((x for x in self.professors if x.professor_id == professor_id), None)
        if not p:
            return "Professor not found"
        students = [s for s in self.students if s.course_id == p.course_id]
        rep = f"\n=== Professor Report: {p.name} ===\n"
        rep += p.professors_details() + "\n"
        rep += f"Students in {p.course_id}: {len(students)}\n"
        return rep


# ============================================================================
# PART 6: MENUS (CLI)
# ============================================================================

def display_menu():
    print("\n" + "=" * 60)
    print("              CheckMyGrade Application")
    print("=" * 60)
    print("1. Student Management")
    print("2. Course Management")
    print("3. Professor Management")
    print("4. Reports")
    print("5. Run Unit Tests")
    print("6. Exit")
    print("=" * 60)


def student_menu(app: CheckMyGrade):
    while True:
        print("\n--- Student Management ---")
        print("1. Add Student")
        print("2. View All Students")
        print("3. Search Student")
        print("4. Update Student")
        print("5. Delete Student")
        print("6. Sort Students")
        print("7. Back")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            try:
                sid = input("Student ID: ").strip()
                fname = input("First Name: ").strip()
                lname = input("Last Name: ").strip()
                email = input("Email: ").strip()
                course = input("Course ID: ").strip()
                grade = input("Grade (or blank): ").strip() or "N/A"
                marks = float(input("Marks (0-100): ") or 0)
                ok = app.add_new_student(Student(sid, fname, lname, email, course, grade, marks))
                print("✓ Student added." if ok else "✗ Student ID already exists.")
            except Exception as e:
                print(f"✗ Error: {e}")

        elif choice == "2":
            app.students = app.fm.load_students()
            if not app.students:
                print("No students.")
            for s in app.students:
                print(s.display_records())

        elif choice == "3":
            field = input("Search by (student_id/email/first_name/last_name/course_id): ").strip()
            value = input(f"Enter {field}: ").strip()
            results, elapsed = app.search_student(field, value)
            print(f"Found {len(results)} results in {elapsed:.4f}s")
            for s in results:
                print(s.display_records())

        elif choice == "4":
            sid = input("Student ID to update: ").strip()
            field = input("Field (first_name,last_name,email,course_id,grade,marks): ").strip()
            value = input("New value: ").strip()
            if field == "marks":
                try:
                    value = float(value)
                except:
                    print("✗ Marks must be numeric.")
                    continue
            ok = app.update_student_record(sid, **{field: value})
            print("✓ Updated." if ok else "✗ Student not found.")

        elif choice == "5":
            sid = input("Student ID to delete: ").strip()
            ok = app.delete_new_student(sid)
            print("✓ Deleted." if ok else "✗ Student not found.")

        elif choice == "6":
            field = input("Sort by (marks/first_name/last_name/email): ").strip()
            desc = input("Descending? (y/n): ").lower() == "y"
            sorted_list, elapsed = app.sort_students(field, desc)
            print(f"Sorted in {elapsed:.4f}s")
            for s in sorted_list:
                print(s.display_records())

        elif choice == "7":
            return


def course_menu(app: CheckMyGrade):
    while True:
        print("\n--- Course Management ---")
        print("1. Add Course")
        print("2. View All Courses")
        print("3. Update Course")
        print("4. Delete Course")
        print("5. Back")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            try:
                cid = input("Course ID: ").strip()
                name = input("Course Name: ").strip()
                desc = input("Description: ").strip()
                credits = int(input("Credits (default 3): ") or 3)
                ok = app.add_new_course(Course(cid, name, desc, credits))
                print("✓ Course added." if ok else "✗ Course ID already exists.")
            except Exception as e:
                print(f"✗ Error: {e}")

        elif choice == "2":
            app.courses = app.fm.load_courses()
            if not app.courses:
                print("No courses.")
            for c in app.courses:
                print(c.display_courses())

        elif choice == "3":
            cid = input("Course ID to update: ").strip()
            field = input("Field (course_name,description,credits): ").strip()
            value = input("New value: ").strip()
            if field == "credits":
                try:
                    value = int(value)
                except:
                    print("✗ Credits must be integer.")
                    continue
            ok = app.update_course(cid, **{field: value})
            print("✓ Updated." if ok else "✗ Course not found.")

        elif choice == "4":
            cid = input("Course ID to delete: ").strip()
            ok = app.delete_new_course(cid)
            print("✓ Deleted." if ok else "✗ Course not found.")

        elif choice == "5":
            return


def professor_menu(app: CheckMyGrade):
    while True:
        print("\n--- Professor Management ---")
        print("1. Add Professor")
        print("2. View All Professors")
        print("3. Update Professor")
        print("4. Delete Professor")
        print("5. Back")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            try:
                pid = input("Professor ID: ").strip()
                name = input("Name: ").strip()
                email = input("Email: ").strip()
                rank = input("Rank: ").strip()
                course = input("Course ID taught: ").strip()
                ok = app.add_new_professor(Professor(pid, name, email, rank, course))
                print("✓ Professor added." if ok else "✗ Professor ID exists.")
            except Exception as e:
                print(f"✗ Error: {e}")

        elif choice == "2":
            app.professors = app.fm.load_professors()
            if not app.professors:
                print("No professors.")
            for p in app.professors:
                print(p.professors_details())

        elif choice == "3":
            pid = input("Professor ID to update: ").strip()
            field = input("Field (name,email,rank,course_id): ").strip()
            value = input("New value: ").strip()
            ok = app.modify_professor_details(pid, **{field: value})
            print("✓ Updated." if ok else "✗ Professor not found.")

        elif choice == "4":
            pid = input("Professor ID to delete: ").strip()
            ok = app.delete_professor(pid)
            print("✓ Deleted." if ok else "✗ Professor not found.")

        elif choice == "5":
            return


def reports_menu(app: CheckMyGrade):
    while True:
        print("\n--- Reports ---")
        print("1. Student Report")
        print("2. Course Report + Stats")
        print("3. Professor Report")
        print("4. Back")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            sid = input("Student ID: ").strip()
            print(app.generate_student_report(sid))

        elif choice == "2":
            cid = input("Course ID: ").strip()
            print(app.generate_course_report(cid))

        elif choice == "3":
            pid = input("Professor ID: ").strip()
            print(app.generate_professor_report(pid))

        elif choice == "4":
            return


# ============================================================================
# PART 7: UNIT TESTS
# ============================================================================

class TestCheckMyGrade(unittest.TestCase):
    def setUp(self):
        self.app = CheckMyGrade("test_data")
        self.app.students = []
        self.app.courses = []
        self.app.professors = []

    def test_1(self):
        s = Student("S001", "John", "Doe", "john@sjsu.edu", "DATA200", "A", 95)
        self.assertTrue(self.app.add_new_student(s))
        self.assertEqual(len(self.app.students), 1)

    def test_duplicate_student_id(self):
        s1 = Student("S001", "A", "B", "a@sjsu.edu", "DATA200", "A", 95)
        s2 = Student("S001", "C", "D", "c@sjsu.edu", "DATA200", "B", 85)
        self.app.add_new_student(s1)
        self.assertFalse(self.app.add_new_student(s2))

    def test_delete_student(self):
        s = Student("S001", "A", "B", "a@sjsu.edu", "DATA200", "A", 95)
        self.app.add_new_student(s)
        self.assertTrue(self.app.delete_new_student("S001"))
        self.assertEqual(len(self.app.students), 0)

    def test_update_student(self):
        s = Student("S001", "A", "B", "a@sjsu.edu", "DATA200", "A", 95)
        self.app.add_new_student(s)
        self.assertTrue(self.app.update_student_record("S001", marks=98, grade="A+"))
        self.assertEqual(self.app.students[0].marks, 98)

    def test_search_student(self):
        s1 = Student("S001", "John", "Doe", "john@sjsu.edu", "DATA200", "A", 95)
        s2 = Student("S002", "Jane", "Smith", "jane@sjsu.edu", "DATA200", "B", 85)
        self.app.add_new_student(s1)
        self.app.add_new_student(s2)
        results, _ = self.app.search_student("first_name", "John")
        self.assertEqual(len(results), 1)

    def test_sort_students(self):
        s1 = Student("S001", "John", "Doe", "john@sjsu.edu", "DATA200", "A", 95)
        s2 = Student("S002", "Jane", "Smith", "jane@sjsu.edu", "DATA200", "B", 85)
        s3 = Student("S003", "Bob", "J", "bob@sjsu.edu", "DATA200", "C", 75)
        self.app.add_new_student(s1)
        self.app.add_new_student(s2)
        self.app.add_new_student(s3)
        sorted_list, elapsed = self.app.sort_students("marks", True)
        self.assertEqual(sorted_list[0].marks, 95)
        self.assertGreaterEqual(elapsed, 0)

    def test_course_stats(self):
        for i in range(5):
            self.app.add_new_student(Student(f"S{i:03d}", f"Stu{i}", "X", f"s{i}@sjsu.edu", "DATA200", "B", 80 + i * 3))
        stats = self.app.get_student_stats("DATA200")
        self.assertTrue(80 <= stats["average"] <= 100)

    def test_course_crud(self):
        c = Course("DATA200", "Data Science", "Intro", 3)
        self.assertTrue(self.app.add_new_course(c))
        self.assertTrue(self.app.update_course("DATA200", course_name="Data Science I"))
        self.assertTrue(self.app.delete_new_course("DATA200"))

    def test_professor_crud(self):
        p = Professor("P001", "Dr. Smith", "smith@sjsu.edu", "Senior", "DATA200")
        self.assertTrue(self.app.add_new_professor(p))
        self.assertTrue(self.app.modify_professor_details("P001", rank="Principal"))
        self.assertTrue(self.app.delete_professor("P001"))

    def test_bulk_students(self):
        for i in range(1000):
            self.app.add_new_student(Student(f"S{i:04d}", "Stu", f"ID{i}", f"s{i}@sjsu.edu", "DATA200", "B", 80))
        self.assertEqual(len(self.app.students), 1000)


# ============================================================================
# PART 8: SIMPLE LOGIN (OPTIONAL/BONUS)
# ============================================================================

def login_flow(fm: FileManager) -> bool:
    print("\n=== Login/Register ===")
    choice = input("1) Login  2) Register  3) Skip -> ").strip()
    if choice == "2":
        uid = input("Email/User ID: ").strip()
        pwd = input("Password: ").strip()
        fm.register_user(uid, pwd, "user")
        print("✓ Registered. You can now login.")
    if choice == "1":
        uid = input("Email/User ID: ").strip()
        pwd = input("Password: ").strip()
        user = fm.load_user(uid)
        if user and user.login(pwd):
            print("✓ Login successful.")
            return True
        print("✗ Invalid credentials.")
        return False
    if choice == "3":
        print("Skipping login (demo mode).")
        return True
    return True


# ============================================================================
# PART 9: MAIN
# ============================================================================

def main():
    app = CheckMyGrade()
    if not login_flow(app.fm):
        return
    while True:
        display_menu()
        choice = input("Enter choice: ").strip()
        if choice == "1":
            student_menu(app)
        elif choice == "2":
            course_menu(app)
        elif choice == "3":
            professor_menu(app)
        elif choice == "4":
            reports_menu(app)
        elif choice == "5":
            print("\nRunning unit tests...\n")
            unittest.main(module=__name__, exit=False, verbosity=2)
        elif choice == "6":
            print("Goodbye, see you soon!")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
