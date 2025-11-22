# gui.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from student_grade_analyzer import GradeAnalyzer, Student
import json
import os

# ---------- Helper dialogs ----------
def ask_string(title, prompt, parent=None, initialvalue=""):
    return simpledialog.askstring(title, prompt, parent=parent, initialvalue=initialvalue)

def ask_float(title, prompt, parent=None, initialvalue=""):
    s = simpledialog.askstring(title, prompt, parent=parent, initialvalue=initialvalue)
    if s is None:
        return None
    try:
        return float(s)
    except ValueError:
        return None

# ---------- GUI App ----------
class GradeAnalyzerGUI:
    def __init__(self, root):
        self.analyzer = GradeAnalyzer()

        # Auto-load on start (silent)
        try:
            self.analyzer.import_json()
        except Exception:
            # If import_json fails for some reason, ignore and continue with empty dataset
            pass

        self.root = root
        self.root.title("Student Grade Analyzer — Phase 3")
        self.root.geometry("1000x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_quit)  # ensure autosave on close

        # Layout frames
        self.top_frame = ttk.Frame(self.root, padding=8)
        self.top_frame.pack(side=TOP, fill=X)

        self.main_frame = ttk.Frame(self.root, padding=(8, 0, 8, 8))
        self.main_frame.pack(side=TOP, fill=BOTH, expand=True)

        self._build_top_bar()
        self._build_main_panes()
        self._build_action_buttons()

        self.refresh_student_list()

    # ---------- Top bar (search + global actions) ----------
    def _build_top_bar(self):
        lbl = ttk.Label(self.top_frame, text="Search:", font=("Segoe UI", 10))
        lbl.pack(side=LEFT, padx=(2, 6))

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(self.top_frame, textvariable=self.search_var)
        search_entry.pack(side=LEFT, fill=X, expand=True)
        search_entry.bind("<KeyRelease>", lambda e: self.on_search_live())

        clear_btn = ttk.Button(self.top_frame, text="Clear", command=self.on_clear_search)
        clear_btn.pack(side=LEFT, padx=6)

        export_btn = ttk.Button(self.top_frame, text="Export (choose file...)", command=self.on_export_dialog)
        export_btn.pack(side=LEFT, padx=(12, 0))

    # ---------- Main panes ----------
    def _build_main_panes(self):
        # Left: student list
        left = ttk.Frame(self.main_frame)
        left.pack(side=LEFT, fill=BOTH, expand=False)

        ttk.Label(left, text="Students", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        columns = ("name", "average", "count")
        self.tree = ttk.Treeview(left, columns=columns, show="headings", height=26)
        self.tree.heading("name", text="Name")
        self.tree.heading("average", text="Average")
        self.tree.heading("count", text="#Grades")
        self.tree.column("name", width=260, anchor="w")
        self.tree.column("average", width=80, anchor="center")
        self.tree.column("count", width=80, anchor="center")

        vsb = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        vsb.pack(side=LEFT, fill=Y)

        self.tree.bind("<<TreeviewSelect>>", self.on_student_selected)
        self.tree.bind("<Double-1>", self.on_student_double_click)

        # Right: details & grade management
        right = ttk.Frame(self.main_frame)
        right.pack(side=RIGHT, fill=BOTH, expand=True)

        ttk.Label(right, text="Details", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        # Student name label
        self.selected_name_var = tk.StringVar(value="No student selected")
        self.selected_name_lbl = ttk.Label(right, textvariable=self.selected_name_var, font=("Segoe UI", 11, "bold"))
        self.selected_name_lbl.pack(anchor="w", pady=(6, 4))

        # Grades listbox with scrollbar
        grades_frame = ttk.Frame(right)
        grades_frame.pack(fill=X, pady=(4, 6))

        self.grades_listbox = tk.Listbox(grades_frame, height=12, activestyle="none", exportselection=False)
        self.grades_listbox.pack(side=LEFT, fill=BOTH, expand=True)

        g_vsb = ttk.Scrollbar(grades_frame, orient="vertical", command=self.grades_listbox.yview)
        self.grades_listbox.configure(yscrollcommand=g_vsb.set)
        g_vsb.pack(side=LEFT, fill=Y)

        # Buttons for grade actions
        grade_btns = ttk.Frame(right)
        grade_btns.pack(fill=X, pady=(6, 8))

        add_grade_btn = ttk.Button(grade_btns, text="Add Grade", command=self.on_add_grade)
        add_grade_btn.grid(row=0, column=0, padx=6, pady=4)

        edit_grade_btn = ttk.Button(grade_btns, text="Edit Grade", command=self.on_edit_grade)
        edit_grade_btn.grid(row=0, column=1, padx=6, pady=4)

        del_grade_btn = ttk.Button(grade_btns, text="Delete Grade", command=self.on_delete_grade, bootstyle="danger")
        del_grade_btn.grid(row=0, column=2, padx=6, pady=4)

        # Statistics
        stats_frame = ttk.Frame(right)
        stats_frame.pack(fill=X, pady=(8, 4))

        self.avg_lbl = ttk.Label(stats_frame, text="Average: -")
        self.avg_lbl.pack(anchor="w")
        self.high_lbl = ttk.Label(stats_frame, text="Highest: -")
        self.high_lbl.pack(anchor="w")
        self.low_lbl = ttk.Label(stats_frame, text="Lowest: -")
        self.low_lbl.pack(anchor="w")
        self.med_lbl = ttk.Label(stats_frame, text="Median: -")
        self.med_lbl.pack(anchor="w")

    # ---------- Bottom action buttons ----------
    def _build_action_buttons(self):
        btn_bar = ttk.Frame(self.root, padding=(8, 8))
        btn_bar.pack(side=BOTTOM, fill=X)

        add_btn = ttk.Button(btn_bar, text="Add Student", bootstyle="success", command=self.on_add_student)
        add_btn.pack(side=LEFT, padx=6)

        rename_btn = ttk.Button(btn_bar, text="Rename Student", bootstyle="info", command=self.on_edit_name)
        rename_btn.pack(side=LEFT, padx=6)

        remove_btn = ttk.Button(btn_bar, text="Remove Student", bootstyle="danger", command=self.on_remove_student)
        remove_btn.pack(side=LEFT, padx=6)

        export_txt_btn = ttk.Button(btn_bar, text="Export TXT", bootstyle="secondary", command=self.on_export_txt)
        export_txt_btn.pack(side=LEFT, padx=6)

        export_csv_btn = ttk.Button(btn_bar, text="Export CSV", bootstyle="secondary", command=self.on_export_csv)
        export_csv_btn.pack(side=LEFT, padx=6)

        refresh_btn = ttk.Button(btn_bar, text="Refresh", bootstyle="light", command=self.refresh_student_list)
        refresh_btn.pack(side=RIGHT, padx=6)

    # ---------- Data & UI sync ----------
    def refresh_student_list(self, filter_query=None):
        # clear tree
        for r in self.tree.get_children():
            self.tree.delete(r)

        students = self.analyzer.students
        keys = sorted(students.keys(), key=lambda n: n.lower())
        for name in keys:
            if filter_query and filter_query.lower() not in name.lower():
                continue
            s = students[name]
            avg_str = f"{s.average():.2f}" if s.grades else "-"
            count = len(s.grades)
            self.tree.insert("", "end", iid=name, values=(name, avg_str, count))

        # clear right panel
        self.clear_details()

    def clear_details(self):
        self.selected_name_var.set("No student selected")
        self.grades_listbox.delete(0, tk.END)
        self.avg_lbl.config(text="Average: -")
        self.high_lbl.config(text="Highest: -")
        self.low_lbl.config(text="Lowest: -")
        self.med_lbl.config(text="Median: -")

    def get_selected_student_name(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return sel[0]

    # ---------- Event handlers ----------
    def on_search_live(self):
        q = self.search_var.get().strip()
        if not q:
            self.refresh_student_list()
        else:
            self.refresh_student_list(filter_query=q)

    def on_clear_search(self):
        self.search_var.set("")
        self.refresh_student_list()

    def on_student_selected(self, event):
        name = self.get_selected_student_name()
        if name:
            self.show_student_details(name)

    def on_student_double_click(self, event):
        # double click toggles show or edit? we'll show details (already done by select)
        name = self.get_selected_student_name()
        if name:
            self.show_student_details(name)

    def show_student_details(self, name):
        student = self.analyzer.students.get(name)
        if not student:
            self.clear_details()
            return

        self.selected_name_var.set(student.name)
        self.grades_listbox.delete(0, tk.END)
        for i, g in enumerate(student.grades, start=1):
            self.grades_listbox.insert(tk.END, f"{i}. {g}")

        if student.grades:
            self.avg_lbl.config(text=f"Average: {student.average():.2f}")
            self.high_lbl.config(text=f"Highest: {student.highest()}")
            self.low_lbl.config(text=f"Lowest: {student.lowest()}")
            self.med_lbl.config(text=f"Median: {student.median()}")
        else:
            self.avg_lbl.config(text="Average: -")
            self.high_lbl.config(text="Highest: -")
            self.low_lbl.config(text="Lowest: -")
            self.med_lbl.config(text="Median: -")

    # ---------- CRUD operations ----------
    def on_add_student(self):
        name = ask_string("Add Student", "Student name:", parent=self.root)
        if name is None:
            return
        name = name.strip()
        if not name:
            messagebox.showwarning("Invalid", "Name cannot be empty.")
            return
        if name in self.analyzer.students:
            messagebox.showwarning("Exists", "Student already exists.")
            return
        self.analyzer.students[name] = Student(name)
        self._autosave()
        self.refresh_student_list()
        # select the new student
        self.tree.selection_set(name)
        self.tree.see(name)

    def on_edit_name(self):
        name = self.get_selected_student_name()
        if not name:
            messagebox.showinfo("Select", "Select a student first.")
            return
        new_name = ask_string("Rename Student", f"New name for '{name}':", parent=self.root, initialvalue=name)
        if new_name is None:
            return
        new_name = new_name.strip()
        if not new_name:
            messagebox.showwarning("Invalid", "Name cannot be empty.")
            return
        if new_name in self.analyzer.students:
            messagebox.showwarning("Conflict", "Another student already uses this name.")
            return
        self.analyzer.students[new_name] = self.analyzer.students.pop(name)
        self.analyzer.students[new_name].name = new_name
        self._autosave()
        self.refresh_student_list()
        self.tree.selection_set(new_name)
        self.tree.see(new_name)

    def on_remove_student(self):
        name = self.get_selected_student_name()
        if not name:
            messagebox.showinfo("Select", "Select a student first.")
            return
        answer = messagebox.askyesno("Confirm", f"Are you sure you want to remove '{name}'?")
        if not answer:
            return
        self.analyzer.students.pop(name, None)
        self._autosave()
        self.refresh_student_list()

    # ---------- Grade operations with modal popups (Option A) ----------
    def on_add_grade(self):
        name = self.get_selected_student_name()
        if not name:
            messagebox.showinfo("Select", "Select a student first.")
            return
        value = ask_float("Add Grade", f"Enter grade for {name} (0-100):", parent=self.root)
        if value is None:
            return
        if not (0 <= value <= 100):
            messagebox.showwarning("Invalid", "Grade must be between 0 and 100.")
            return
        student = self.analyzer.students.get(name)
        if student is None:
            messagebox.showerror("Error", "Selected student not found.")
            return
        student.add_grade(value)
        self._autosave()
        self.show_student_details(name)
        self.refresh_student_list()

    def on_edit_grade(self):
        name = self.get_selected_student_name()
        if not name:
            messagebox.showinfo("Select", "Select a student and a grade first.")
            return
        idx = self.grades_listbox.curselection()
        if not idx:
            messagebox.showinfo("Select", "Select a grade from the list to edit.")
            return
        sel_index = idx[0]  # listbox index
        student = self.analyzer.students.get(name)
        if student is None:
            messagebox.showerror("Error", "Selected student not found.")
            return
        current_value = student.grades[sel_index]
        new_value = ask_float("Edit Grade", f"Edit grade (0-100) for {name}:", parent=self.root, initialvalue=str(current_value))
        if new_value is None:
            return
        if not (0 <= new_value <= 100):
            messagebox.showwarning("Invalid", "Grade must be between 0 and 100.")
            return
        student.grades[sel_index] = new_value
        self._autosave()
        self.show_student_details(name)
        self.refresh_student_list()
        # re-select edited grade
        self.grades_listbox.selection_clear(0, tk.END)
        self.grades_listbox.selection_set(sel_index)
        self.grades_listbox.see(sel_index)

    def on_delete_grade(self):
        name = self.get_selected_student_name()
        if not name:
            messagebox.showinfo("Select", "Select a student and a grade first.")
            return
        idx = self.grades_listbox.curselection()
        if not idx:
            messagebox.showinfo("Select", "Select a grade from the list to delete.")
            return
        sel_index = idx[0]
        student = self.analyzer.students.get(name)
        if student is None:
            messagebox.showerror("Error", "Selected student not found.")
            return
        confirm = messagebox.askyesno("Confirm", f"Delete grade #{sel_index+1} ({student.grades[sel_index]}) for {name}?")
        if not confirm:
            return
        student.grades.pop(sel_index)
        self._autosave()
        self.show_student_details(name)
        self.refresh_student_list()

    # ---------- Exports ----------
    def on_export_txt(self):
        try:
            # let user choose path
            fname = filedialog.asksaveasfilename(title="Save text report", defaultextension=".txt", filetypes=[("Text files","*.txt"),("All files","*.*")])
            if not fname:
                return
            # temporarily call export_report but write to chosen file
            content_lines = []
            content_lines.append("STUDENT GRADE REPORT")
            content_lines.append("====================")
            content_lines.append("")
            for student in self.analyzer.students.values():
                content_lines.append(f"Name: {student.name}")
                content_lines.append(f"Grades: {student.grades}")
                content_lines.append(f"Average: {student.average():.2f}")
                content_lines.append(f"Highest: {student.highest()}")
                content_lines.append(f"Lowest: {student.lowest()}")
                content_lines.append(f"Median: {student.median()}")
                content_lines.append("-" * 30)
            with open(fname, "w") as fh:
                fh.write("\n".join(content_lines))
            messagebox.showinfo("Export", f"Text report saved to:\n{fname}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def on_export_csv(self):
        try:
            fname = filedialog.asksaveasfilename(title="Save CSV report", defaultextension=".csv", filetypes=[("CSV files","*.csv"),("All files","*.*")])
            if not fname:
                return
            # write CSV similar to export_report_csv but to chosen filename
            with open(fname, "w") as f:
                f.write("name,grade,average,highest,lowest,median\n")
                for student in self.analyzer.students.values():
                    if not student.grades:
                        f.write(f"{student.name},,,,\n")
                        continue
                    for g in student.grades:
                        f.write(
                            f"{student.name},"
                            f"{g},"
                            f"{student.average():.2f},"
                            f"{student.highest()},"
                            f"{student.lowest()},"
                            f"{student.median()}\n"
                        )
            messagebox.showinfo("Export", f"CSV report saved to:\n{fname}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def on_export_dialog(self):
        # small chooser to pick txt or csv (user friendly)
        choice = messagebox.askquestion("Export", "Export as CSV? (No = TXT)")
        if choice == "yes":
            self.on_export_csv()
        else:
            self.on_export_txt()

    # ---------- Autosave helper ----------
    def _autosave(self):
        # tries analyzer.autosave() then falls back to export_json()
        try:
            # method used earlier in backend
            if hasattr(self.analyzer, "autosave"):
                self.analyzer.autosave()
            else:
                self.analyzer.export_json()
        except Exception:
            # best-effort fallback: attempt save_to_json from data_manager if exists
            try:
                self.analyzer.export_json()
            except Exception:
                # last resort: silently ignore but alert user when quitting if needed
                pass

    # ---------- Quit handler ----------
    def on_quit(self):
        # final autosave
        self._autosave()
        self.root.destroy()

# ---------- Run ----------
def main():
    root = tb.Window(themename="litera")  # change theme if you like
    app = GradeAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
