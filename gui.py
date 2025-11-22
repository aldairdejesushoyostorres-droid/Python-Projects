import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from student_grade_analyzer import GradeAnalyzer, Student
import os

# ---------------------------
# Helper UI dialogs
# ---------------------------

def ask_string(title, prompt, parent=None):
    return simpledialog.askstring(title, prompt, parent=parent)

def ask_float(title, prompt, parent=None):
    s = simpledialog.askstring(title, prompt, parent=parent)
    if s is None:
        return None
    try:
        return float(s)
    except ValueError:
        return None

# ---------------------------
# Main GUI Application
# ---------------------------

class GradeAnalyzerGUI:
    def __init__(self, root):
        # backend analyzer instance
        self.analyzer = GradeAnalyzer()

        # auto-load existing data (if any)
        # GradeAnalyzer.import_json() uses the data_manager loader
        try:
            # call the method that loads from default filename
            self.analyzer.import_json()
        except Exception:
            # safe guard in case import_json not present or fails
            pass

        # setup UI
        self.root = root
        self.root.title("Student Grade Analyzer")
        self.root.geometry("900x540")

        # layout frames (left: list, right: details + buttons)
        self.left_frame = ttk.Frame(self.root, padding=(10, 10, 5, 10))
        self.left_frame.pack(side=LEFT, fill=BOTH, expand=False)

        self.right_frame = ttk.Frame(self.root, padding=(5, 10, 10, 10))
        self.right_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        self._build_left()
        self._build_right()
        self._build_bottom_buttons()

        # Populate list
        self.refresh_student_list()

    # ---------------------------
    # Left: student list (Treeview)
    # ---------------------------
    def _build_left(self):
        lbl = ttk.Label(self.left_frame, text="Students", font=("Segoe UI", 12, "bold"))
        lbl.pack(anchor="w")

        cols = ("name", "average", "count")
        self.tree = ttk.Treeview(self.left_frame, columns=cols, show="headings", height=20)
        self.tree.heading("name", text="Name")
        self.tree.heading("average", text="Average")
        self.tree.heading("count", text="#Grades")
        self.tree.column("name", width=200, anchor="w")
        self.tree.column("average", width=80, anchor="center")
        self.tree.column("count", width=60, anchor="center")
        self.tree.pack(fill=BOTH, expand=True)

        # bind selection
        self.tree.bind("<<TreeviewSelect>>", self.on_student_selected)

        # small search box above list
        search_frame = ttk.Frame(self.left_frame)
        search_frame.pack(fill="x", pady=(8, 0))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=LEFT, fill="x", expand=True)
        search_button = ttk.Button(search_frame, text="Search", command=self.on_search)
        search_button.pack(side=LEFT, padx=(6, 0))

    # ---------------------------
    # Right: details panel
    # ---------------------------
    def _build_right(self):
        title = ttk.Label(self.right_frame, text="Student Details", font=("Segoe UI", 12, "bold"))
        title.pack(anchor="w")

        # grades list
        self.grades_listbox = tk.Listbox(self.right_frame, height=12)
        self.grades_listbox.pack(fill="x", pady=(8, 6))

        # stats
        stats_frame = ttk.Frame(self.right_frame)
        stats_frame.pack(fill="x")

        self.avg_lbl = ttk.Label(stats_frame, text="Average: -")
        self.avg_lbl.pack(anchor="w")

        self.high_lbl = ttk.Label(stats_frame, text="Highest: -")
        self.high_lbl.pack(anchor="w")

        self.low_lbl = ttk.Label(stats_frame, text="Lowest: -")
        self.low_lbl.pack(anchor="w")

        self.med_lbl = ttk.Label(stats_frame, text="Median: -")
        self.med_lbl.pack(anchor="w")

    # ---------------------------
    # Bottom buttons
    # ---------------------------
    def _build_bottom_buttons(self):
        btn_frame = ttk.Frame(self.right_frame, padding=(0, 12, 0, 0))
        btn_frame.pack(fill="x", side=BOTTOM)

        add_btn = ttk.Button(btn_frame, text="Add Student", bootstyle="success", command=self.on_add_student)
        add_btn.grid(row=0, column=0, padx=6, pady=6)

        remove_btn = ttk.Button(btn_frame, text="Remove Student", bootstyle="danger", command=self.on_remove_student)
        remove_btn.grid(row=0, column=1, padx=6, pady=6)

        add_grade_btn = ttk.Button(btn_frame, text="Add Grade", bootstyle="primary", command=self.on_add_grade)
        add_grade_btn.grid(row=0, column=2, padx=6, pady=6)

        edit_name_btn = ttk.Button(btn_frame, text="Edit Name", bootstyle="info", command=self.on_edit_name)
        edit_name_btn.grid(row=0, column=3, padx=6, pady=6)

        export_txt_btn = ttk.Button(btn_frame, text="Export TXT", bootstyle="secondary", command=self.on_export_txt)
        export_txt_btn.grid(row=1, column=0, padx=6, pady=6)

        export_csv_btn = ttk.Button(btn_frame, text="Export CSV", bootstyle="secondary", command=self.on_export_csv)
        export_csv_btn.grid(row=1, column=1, padx=6, pady=6)

        refresh_btn = ttk.Button(btn_frame, text="Refresh", bootstyle="light", command=self.refresh_student_list)
        refresh_btn.grid(row=1, column=2, padx=6, pady=6)

        quit_btn = ttk.Button(btn_frame, text="Quit", bootstyle="danger-outline", command=self.on_quit)
        quit_btn.grid(row=1, column=3, padx=6, pady=6)

    # ---------------------------
    # Events & Actions
    # ---------------------------
    def refresh_student_list(self, filter_query=None):
        # Clear tree
        for r in self.tree.get_children():
            self.tree.delete(r)

        # Re-populate
        students = self.analyzer.students
        keys = sorted(students.keys(), key=lambda n: n.lower())
        for name in keys:
            if filter_query:
                if filter_query.lower() not in name.lower():
                    continue
            s = students[name]
            avg = f"{s.average():.2f}" if s.grades else "-"
            count = len(s.grades)
            self.tree.insert("", "end", iid=name, values=(name, avg, count))

        # clear right panel
        self.clear_details()

    def clear_details(self):
        self.grades_listbox.delete(0, tk.END)
        self.avg_lbl.config(text="Average: -")
        self.high_lbl.config(text="Highest: -")
        self.low_lbl.config(text="Lowest: -")
        self.med_lbl.config(text="Median: -")

    def on_student_selected(self, event):
        sel = self.tree.selection()
        if not sel:
            self.clear_details()
            return
        name = sel[0]
        self.show_student_details(name)

    def show_student_details(self, name):
        student = self.analyzer.students.get(name)
        if not student:
            self.clear_details()
            return

        # update grades listbox
        self.grades_listbox.delete(0, tk.END)
        for i, g in enumerate(student.grades, start=1):
            self.grades_listbox.insert(tk.END, f"{i}. {g}")

        # update stats
        self.avg_lbl.config(text=f"Average: {student.average():.2f}" if student.grades else "Average: -")
        self.high_lbl.config(text=f"Highest: {student.highest()}" if student.grades else "Highest: -")
        self.low_lbl.config(text=f"Lowest: {student.lowest()}" if student.grades else "Lowest: -")
        self.med_lbl.config(text=f"Median: {student.median()}" if student.grades else "Median: -")

    def get_selected_student_name(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return sel[0]

    # ---------------------------
    # Button handlers
    # ---------------------------
    def on_add_student(self):
        name = ask_string("Add Student", "Student name:", parent=self.root)
        if not name:
            return
        name = name.strip()
        if not name:
            messagebox.showwarning("Invalid", "Name cannot be empty.")
            return
        if name in self.analyzer.students:
            messagebox.showwarning("Already exists", "A student with that name already exists.")
            return
        # add using backend structure and autosave
        self.analyzer.students[name] = Student(name)
        try:
            self.analyzer.autosave()
        except Exception:
            # fallback to calling export_json if autosave not defined
            try:
                self.analyzer.export_json()
            except Exception:
                pass
        self.refresh_student_list()

    def on_remove_student(self):
        name = self.get_selected_student_name()
        if not name:
            messagebox.showinfo("Select student", "Please select a student to remove.")
            return
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to remove '{name}'?")
        if not confirm:
            return
        self.analyzer.students.pop(name, None)
        # save
        try:
            self.analyzer.autosave()
        except Exception:
            try:
                self.analyzer.export_json()
            except Exception:
                pass
        self.refresh_student_list()

    def on_add_grade(self):
        name = self.get_selected_student_name()
        if not name:
            messagebox.showinfo("Select student", "Please select a student to add a grade.")
            return
        g = ask_float("Add Grade", f"Enter grade for {name} (0-100):", parent=self.root)
        if g is None:
            return
        if g < 0 or g > 100:
            messagebox.showwarning("Invalid", "Grade must be between 0 and 100.")
            return
        student = self.analyzer.students.get(name)
        if student is None:
            return
        student.add_grade(g)
        # save
        try:
            self.analyzer.autosave()
        except Exception:
            try:
                self.analyzer.export_json()
            except Exception:
                pass
        self.show_student_details(name)
        self.refresh_student_list()

    def on_edit_name(self):
        name = self.get_selected_student_name()
        if not name:
            messagebox.showinfo("Select student", "Please select a student to rename.")
            return
        new_name = ask_string("Edit Name", f"Enter new name for '{name}':", parent=self.root)
        if not new_name:
            return
        new_name = new_name.strip()
        if not new_name:
            messagebox.showwarning("Invalid", "Name cannot be empty.")
            return
        if new_name in self.analyzer.students:
            messagebox.showwarning("Conflict", "Another student already uses this name.")
            return
        # rename
        self.analyzer.students[new_name] = self.analyzer.students.pop(name)
        self.analyzer.students[new_name].name = new_name
        # save
        try:
            self.analyzer.autosave()
        except Exception:
            try:
                self.analyzer.export_json()
            except Exception:
                pass
        self.refresh_student_list()

    def on_export_txt(self):
        # call backend export_report
        try:
            self.analyzer.export_report()
            messagebox.showinfo("Export", "Text report exported successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")

    def on_export_csv(self):
        try:
            self.analyzer.export_report_csv()
            messagebox.showinfo("Export", "CSV report exported successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")

    def on_search(self):
        q = self.search_var.get().strip()
        if not q:
            self.refresh_student_list()
            return
        # filter and refresh
        self.refresh_student_list(filter_query=q)

    def on_quit(self):
        # final autosave
        try:
            self.analyzer.autosave()
        except Exception:
            try:
                self.analyzer.export_json()
            except Exception:
                pass
        self.root.quit()

# ---------------------------
# Run the app
# ---------------------------
def main():
    root = tb.Window(themename="litera")  # choose a theme you like
    app = GradeAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
