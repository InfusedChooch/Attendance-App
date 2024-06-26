import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json
import csv
from datetime import datetime
import os
from pathlib import Path

ctk.set_appearance_mode("Dark")  # Automatic light/dark mode
ctk.set_default_color_theme("blue")  # Default color theme

class CheckInApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Check-In System")
        self.geometry("500x250")

        # Load attendance data and classes from JSON file
        self.attendance_data = self.load_attendance_data()
        self.classes = self.load_classes_from_json()

        if not self.classes:
            self.classes = ["No Classes Found"]

        # Initialize the UI components
        self.initialize_ui()

    def initialize_ui(self):
        """Initialize all the UI components."""
        self.create_class_selection_dropdown()
        self.create_name_entry_dropdown()
        self.create_check_in_button()
        self.create_audit_log_button()
        self.update_name_dropdown()  # Populate name dropdown based on the first class

    def create_class_selection_dropdown(self):
        """Create and set up the class selection dropdown."""
        self.class_label = ctk.CTkLabel(self, text="Select Class:")
        self.class_label.pack(pady=(5, 0))

        self.selected_class = tk.StringVar()
        self.class_selection = ctk.CTkComboBox(self, values=self.classes, variable=self.selected_class, width=200)
        self.class_selection.set(self.classes[0] if self.classes else "Select Class")
        self.class_selection.pack(pady=(0, 5))
        self.selected_class.trace_add("write", self.update_name_dropdown)

    def create_name_entry_dropdown(self):
        """Create and set up the name entry dropdown and entry field."""
        self.name_dropdown_label = ctk.CTkLabel(self, text="Select or Type name:")
        self.name_dropdown_label.pack(pady=(5, 0))

        self.selected_name = tk.StringVar()
        self.name_dropdown = ctk.CTkComboBox(self, variable=self.selected_name, width=400)
        self.name_dropdown.pack(pady=5)
        self.name_dropdown.bind('<Return>', self.check_in)

        self.name_entry = ctk.CTkEntry(self, width=400)
        self.name_entry.bind('<Return>', self.check_in)

    def create_check_in_button(self):
        """Create the check-in button."""
        self.check_in_button = ctk.CTkButton(self, text="Check In", command=self.check_in)
        self.check_in_button.pack(pady=(10, 0))

    def create_audit_log_button(self):
        """Create the audit log button."""
        self.audit_button = ctk.CTkButton(self, text="Audit Log", command=self.audit_log)
        self.audit_button.pack(pady=(20, 0))

    def get_data_file_path(self):
        """Get the path to the data file. Create it if it doesn't exist."""
        desktop_path = Path.home() / 'Desktop'
        data_directory = desktop_path / 'DataAT2'
        os.makedirs(data_directory, exist_ok=True)
        file_path = data_directory / 'attendance_log.json'
        if not file_path.exists():
            with open(file_path, 'w') as file:
                json.dump({}, file)
        return file_path

    def load_attendance_data(self):
        """Load attendance data from the JSON file."""
        file_path = self.get_data_file_path()
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return json.load(file)
        return {}

    def refresh_app(self):
        """Refresh the application by reloading class and name lists."""
        self.classes = self.load_classes_from_json()

        self.class_selection.configure(values=self.classes)
        if self.classes:
            self.class_selection.set(self.classes[0])
        else:
            self.class_selection.set("No Classes Found")

        self.update_name_dropdown()
        self.name_entry.delete(0, tk.END)
        self.selected_name.set("")
        self.update_audit_log()

    def update_name_dropdown(self, *args):
        """Update the names dropdown based on the selected class."""
        selected_class = self.selected_class.get()
        file_path = self.get_data_file_path()
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
            if selected_class in data:
                names = list(data[selected_class].keys())
            else:
                names = []
            self.name_dropdown.configure(values=names)
            if names:
                self.name_dropdown.set(names[0])
            else:
                self.name_dropdown.set('')
        except FileNotFoundError:
            messagebox.showwarning("File Not Found", "The attendance_log.json file could not be found.")
        except json.JSONDecodeError:
            messagebox.showwarning("JSON Error", "There was an error reading the JSON file.")

    def load_classes_from_json(self):
        """Load classes from the JSON file."""
        file_path = self.get_data_file_path()
        classes = []
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
            classes = list(data.keys())
        except FileNotFoundError:
            messagebox.showwarning("File Not Found", "The attendance_log.json file could not be found.")
        except json.JSONDecodeError:
            messagebox.showwarning("JSON Error", "There was an error reading the JSON file.")
        return classes

    def check_in(self, event=None):
        """Handle the check-in process for a student."""
        selected_name_dropdown = self.selected_name.get().strip().title()
        entered_name = self.name_entry.get().strip().title()

        full_name = selected_name_dropdown if selected_name_dropdown else entered_name

        if not full_name:
            messagebox.showwarning("Missing Name", "Please enter your name or select it from the dropdown before checking in.")
            return

        selected_class = self.selected_class.get()
        date_str = datetime.now().strftime("%Y-%m-%d")
        time_str = datetime.now().strftime("%H:%M:%S")

        file_path = self.get_data_file_path()
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                data = json.load(file)
        else:
            data = {}

        if selected_class not in data:
            data[selected_class] = {}
        if full_name not in data[selected_class]:
            data[selected_class][full_name] = {"Check-in": []}

        data[selected_class][full_name]["Check-in"].append({"Date": date_str, "Time": time_str})

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

        messagebox.showinfo("Success", f"{full_name} has successfully checked in for {selected_class}.")
        self.name_entry.delete(0, tk.END)
        self.attendance_data = self.load_attendance_data()
        self.update_audit_log()

    def open_management_window(self):
        """Open the class management window."""
        management_window = ctk.CTkToplevel(self)
        management_window.title("Class Management & Export")
        management_window.geometry("400x400")

        self.create_management_widgets(management_window)

    def create_management_widgets(self, window):
        """Create widgets for class management in the management window."""
        # Add Class Widgets
        add_class_label = ctk.CTkLabel(window, text="Add New Class:")
        add_class_label.pack(pady=(10, 0))
        self.add_class_entry = ctk.CTkEntry(window, width=300)
        self.add_class_entry.pack(pady=5)
        add_class_button = ctk.CTkButton(window, text="Add Class", command=self.add_custom_class)
        add_class_button.pack(pady=(5, 0))

        # Remove Class Widgets
        remove_class_label = ctk.CTkLabel(window, text="Remove Class:")
        remove_class_label.pack(pady=(10, 0))
        self.remove_class_selection = tk.StringVar()
        self.remove_class_dropdown = ctk.CTkComboBox(window, values=self.classes, variable=self.remove_class_selection)
        self.remove_class_dropdown.pack(pady=5)
        remove_class_button = ctk.CTkButton(window, text="Remove Class", command=self.remove_class)
        remove_class_button.pack(pady=(5, 0))

        # CSV Conversion Button
        csv_conversion_button = ctk.CTkButton(window, text="Convert CSV to JSON", command=self.select_file)
        csv_conversion_button.pack(pady=(10, 0))

        # Course Appendix Slider
        self.course_appendix_label = ctk.CTkLabel(window, text="Append MHS = 7")
        self.course_appendix_label.pack(pady=(10, 0))
        self.course_appendix_slider = ctk.CTkSlider(window, from_=0, to=10, number_of_steps=10)
        self.course_appendix_slider.set(7)  # Default value
        self.course_appendix_slider.pack(pady=(0, 10))
        self.slider_value_label = ctk.CTkLabel(window, text="Slider Value: 1")
        self.slider_value_label.pack()
        self.update_slider_value_label()

    def update_slider_value_label(self):
        """Update the label with the current value of the slider."""
        current_value = self.course_appendix_slider.get()
        self.slider_value_label.configure(text=f"Slider Value: {current_value}")
        self.after(100, self.update_slider_value_label)

    def convert_csv(self, input_file):
        """Convert a CSV file to a dictionary."""
        converted_data = []
        appendix_value = int(self.course_appendix_slider.get())
        with open(input_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                course = row['Course'][appendix_value:].title()
                student = f"{row['First Name']} {row['Last Name']}".title()
                gender = row['Gender'].capitalize()
                grade = row['Grade']
                converted_data.append({'Course': course, 'Full Name': student, 'Gender': gender, 'Grade': grade, 'Check-in': []})
        return converted_data

    def save_csv(self, data):
        """Save data to a CSV file."""
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        folder_path = os.path.join(desktop_path, 'DataAT2')
        os.makedirs(folder_path, exist_ok=True)
        file_name = "converted_attendance_export.csv"
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Course", "Student", "Gender", "Grade", "Date", "Status"])
            for item in data:
                writer.writerow([item['Course'], item['Full Name'], item['Gender'], item['Grade'], '', ''])
        return file_path

    def convert_to_json(self, data):
        """Convert a list of dictionaries to a nested JSON structure."""
        json_data = {}
        for record in data:
            course = record['Course']
            full_name = record['Full Name']
            if course not in json_data:
                json_data[course] = {}
            if full_name not in json_data[course]:
                json_data[course][full_name] = {'Check-in': []}
        return json_data

    def save_json(self, data):
        """Save data to a JSON file."""
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        folder_path = os.path.join(desktop_path, 'DataAT2')
        os.makedirs(folder_path, exist_ok=True)
        file_name = "attendance_log.json"
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        return file_path

    def select_file(self):
        """Select a CSV file for conversion to JSON."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            converted_data = self.convert_csv(file_path)
            saved_file_path_csv = self.save_csv(converted_data)
            json_data = self.convert_to_json(converted_data)
            saved_file_path_json = self.save_json(json_data)
            messagebox.showinfo("Conversion Successful", f"CSV file converted and saved to:\n{saved_file_path_csv}\n\nJSON file saved to:\n{saved_file_path_json}")

    def add_custom_class(self):
        """Add a new class to the list of classes."""
        new_class = self.add_class_entry.get().strip()
        if new_class and new_class not in self.classes:
            self.classes.append(new_class)
            self.class_selection.configure(values=self.classes)
            self.remove_class_dropdown.configure(values=self.classes)
            messagebox.showinfo("Success", f"Class '{new_class}' added.")
            self.add_class_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Class already exists or field is empty.")

    def remove_class(self):
        """Remove a class from the list of classes."""
        class_to_remove = self.remove_class_selection.get()
        if class_to_remove in self.classes:
            self.classes.remove(class_to_remove)
            self.class_selection.configure(values=self.classes)
            self.remove_class_dropdown.configure(values=self.classes)

            file_path = self.get_data_file_path()
            with open(file_path, "r") as file:
                data = json.load(file)

            if class_to_remove in data:
                del data[class_to_remove]

                with open(file_path, "w") as file:
                    json.dump(data, file, indent=4)

            self.refresh_app()
            messagebox.showinfo("Success", f"Class '{class_to_remove}' removed.")
        else:
            messagebox.showwarning("Warning", "Please select a valid class to remove.")

    def export_data(self):
        """Export attendance data to a text file."""
        file_path = self.get_data_file_path()
        self.generate_report(file_path, file_path.with_suffix('.txt'))

    def generate_report(self, file_path, output_file):
        """Generate a report of attendance data."""
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "File does not exist.")
            return

        with open(file_path, "r") as file:
            data = json.load(file)

        with open(output_file, "w") as report:
            for class_name, students in data.items():
                report.write(f"Class: {class_name}\n")
                for student_name, attendance in students.items():
                    num_logins = len(attendance["Check-in"])
                    report.write(f"{student_name}: {num_logins} logins\n")
                report.write("\n")

        messagebox.showinfo("Report Generated", "The report has been successfully generated.")

    def audit_log(self):
        """Open the audit log window to display today's check-ins."""
        if not hasattr(self, 'audit_window') or not self.audit_window.winfo_exists():
            self.audit_window = ctk.CTkToplevel(self)
            self.audit_window.title("Audit Log - Today's Check-Ins")
            self.audit_window.geometry("800x800")

            button_frame = ctk.CTkFrame(self.audit_window)
            button_frame.pack(pady=20)

            button1 = ctk.CTkButton(button_frame, text="Export Data", command=self.export_data)
            button2 = ctk.CTkButton(button_frame, text="Refresh", command=self.refresh_app)
            button3 = ctk.CTkButton(button_frame, text="Management", command=self.open_management_window)

            button1.pack(side="left", padx=10)
            button2.pack(side="left", padx=10)
            button3.pack(side="left", padx=10)

            sort_frame = ctk.CTkFrame(self.audit_window)
            sort_frame.pack(pady=10)

            sort_date_time_desc = ctk.CTkButton(sort_frame, text="Sort by Date & Time (Desc)", command=lambda: self.update_audit_log(sort_key="date_time_desc"))
            sort_date_time_asc = ctk.CTkButton(sort_frame, text="Sort by Date & Time (Asc)", command=lambda: self.update_audit_log(sort_key="date_time_asc"))
            sort_student_name = ctk.CTkButton(sort_frame, text="Sort by Student Name", command=lambda: self.update_audit_log(sort_key="student_name"))
            sort_course = ctk.CTkButton(sort_frame, text="Sort by Course", command=lambda: self.update_audit_log(sort_key="course"))

            sort_date_time_desc.pack(side="left", padx=10)
            sort_date_time_asc.pack(side="left", padx=10)
            sort_student_name.pack(side="left", padx=10)
            sort_course.pack(side="left", padx=10)

            self.result_area = scrolledtext.ScrolledText(self.audit_window, width=600, height=80)
            self.result_area.pack(pady=20)

        self.update_audit_log()

    def update_audit_log(self, sort_key="date_time_desc"):
        """Update the audit log display based on the selected sort key."""
        if self.result_area:
            self.result_area.delete('1.0', 'end')
            today = datetime.now().strftime("%Y-%m-%d")
            check_in_entries = []

            for course, students in self.attendance_data.items():
                for student, details in students.items():
                    for record in details['Check-in']:
                        if record['Date'] == today:
                            time = record['Time']
                            check_in_entries.append((today, time, student, course))

            if sort_key == "date_time_desc":
                check_in_entries.sort(key=lambda entry: (entry[0], entry[1]), reverse=True)
            elif sort_key == "date_time_asc":
                check_in_entries.sort(key=lambda entry: (entry[0], entry[1]))
            elif sort_key == "student_name":
                check_in_entries.sort(key=lambda entry: entry[2])
            elif sort_key == "course":
                check_in_entries.sort(key=lambda entry: entry[3])

            output_text = [f"{entry[2]} ({entry[3]}) - Checked in on {entry[0]} at {entry[1]}\n" for entry in check_in_entries]
            if output_text:
                self.result_area.insert('end', ''.join(output_text))
            else:
                self.result_area.insert('end', "No check-ins for today.")

def main():
    app = CheckInApp()
    app.mainloop()

if __name__ == "__main__":
    main()
