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
   
    def get_data_file_path(self):
        desktop_path = Path.home() / 'Desktop'
        data_directory = desktop_path / 'DataAT2'
        # Ensure the directory exists
        os.makedirs(data_directory, exist_ok=True)
        file_path = data_directory / 'attendance_log.json'
        # Check if the file exists, if not, create it with default content
        if not file_path.exists():
            with open(file_path, 'w') as file:
                # Assuming default content is an empty dictionary
                # You might adjust this based on your needs
                json.dump({}, file)
        return file_path
    
    def __init__(self):
        super().__init__()
        self.title("Check-In System")
        self.geometry("600x380")
    
        #load Data from
        self.attendance_data = self.load_attendance_data()

       # Load class / name list from JSON
        self.classes = self.load_classes_from_json()
        self.names = ["Select"]

        # If no classes found, you can set a default list or handle accordingly
        if not self.classes:
            self.classes = ["No Classes Found"]

        # Class Selection Dropdown
        self.class_label = ctk.CTkLabel(self, text="Select Class:")
        self.class_label.pack(pady=(5, 0))
        self.selected_class = tk.StringVar()
        self.class_selection = ctk.CTkComboBox(self, values=self.classes, variable=self.selected_class, width=200)
        self.class_selection.set(self.classes[0] if self.classes else "Select Class")  # Set default value or a placeholder
        self.class_selection.pack(pady=(0, 5))
        self.selected_class.trace_add("write", self.update_name_dropdown)

        # Name Dropdown (initially empty)
        self.name_dropdown_label = ctk.CTkLabel(self, text="Select or Type name:")
        self.name_dropdown_label.pack(pady=(5, 0))
    
        self.selected_name = tk.StringVar()
        self.name_dropdown = ctk.CTkComboBox(self, variable=self.selected_name, width=400)
        self.name_dropdown.pack(pady=5)
        self.name_dropdown.bind('<Return>' , self.check_in)
        
        # Name Entry
       # self.name_label = ctk.CTkLabel(self, text="Or Type Your Name:")
       # self.name_label.pack(pady=(10, 0))
        self.name_entry = ctk.CTkEntry(self, width=400)
        #self.name_entry.pack(pady=5)
        self.name_entry.bind('<Return>', self.check_in)

        # Check-In Button
        self.check_in_button = ctk.CTkButton(self, text="Check In", command=self.check_in)
        self.check_in_button.pack(pady=(10, 0))

        # Management Button
        self.manage_classes_button = ctk.CTkButton(self, text="Manage Classes & Export", command=self.open_management_window)
        self.manage_classes_button.pack(pady=(5, 0))

        # Refresh Button
        self.refresh_button = ctk.CTkButton(self, text="Refresh App", command=self.refresh_app)
        self.refresh_button.pack(pady=(10, 0))
        
        # Audit Log
        self.manage_classes_button = ctk.CTkButton(self, text="Audit Log", command=self.audit_log)
        self.manage_classes_button.pack(pady=(5, 0))

        # Call update_name_dropdown initially to populate names based on the first class
        self.update_name_dropdown()

        # Initially populate the name dropdown based on the first class
        self.update_name_dropdown()

    def load_attendance_data(self):
        file_path = self.get_data_file_path()
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return json.load(file)
        else:
            return {}

    def refresh_app(self):
        # Reload class and name lists from JSON
        self.classes = self.load_classes_from_json()
        self.names = ["Select"]
        
        # Update class selection dropdown
        self.class_selection.configure(values=self.classes)
        if self.classes:
            self.class_selection.set(self.classes[0])
        else:
            self.class_selection.set("No Classes Found")
        
        # Update name selection dropdown
        self.update_name_dropdown()

        # Optionally, clear any existing selections or input
        self.name_entry.delete(0, tk.END)
        self.selected_name.set("")

    def update_slider_value_label(self):
        current_value = self.course_appendix_slider.get()
        self.slider_value_label.configure(text=f"Slider Value: {current_value}")
        self.after(100, self.update_slider_value_label)  # Schedule this method to be called every 100ms

    def update_name_dropdown(self, *args):
        selected_class = self.selected_class.get()
        file_path = self.get_data_file_path()
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
            if selected_class in data:
                names = list(data[selected_class].keys())
            else:
                names = []
            self.name_dropdown.configure(values=names)  # Update the list of values
            if names:
                self.name_dropdown.set(names[0])  # Optionally set to first name
            else:
                self.name_dropdown.set('')  # Clear if no names
        except FileNotFoundError:
            messagebox.showwarning("File Not Found", "The attendance_log.json file could not be found.", "Please covert a file")
        except json.JSONDecodeError:
            messagebox.showwarning("JSON Error", "There was an error reading the JSON file.")

    def load_classes_from_json(self):
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
        selected_name_dropdown = self.selected_name.get().strip().title() if self.names else ""
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
    
    def open_management_window(self):
        management_window = ctk.CTkToplevel(self)
        management_window.title("Class Management & Export")
        management_window.geometry("400x400")

        # Add Class Widgets
        add_class_label = ctk.CTkLabel(management_window, text="Add New Class:")
        add_class_label.pack(pady=(10, 0))
        self.add_class_entry = ctk.CTkEntry(management_window, width=300)
        self.add_class_entry.pack(pady=5)
        add_class_button = ctk.CTkButton(management_window, text="Add Class", command=self.add_custom_class)
        add_class_button.pack(pady=(5, 0))

        # Remove Class Widgets
        remove_class_label = ctk.CTkLabel(management_window, text="Remove Class:")
        remove_class_label.pack(pady=(10, 0))
        self.remove_class_selection = tk.StringVar()
        self.remove_class_dropdown = ctk.CTkComboBox(management_window, values=self.classes, variable=self.remove_class_selection)
        self.remove_class_dropdown.pack(pady=5)
        remove_class_button = ctk.CTkButton(management_window, text="Remove Class", command=self.remove_class)
        remove_class_button.pack(pady=(5, 0))
        
        
        #CSV Conversion Button
        csv_conversion_button = ctk.CTkButton(management_window, text="Convert CSV to JSON", command=self.select_file)
        csv_conversion_button.pack(pady=(10, 0))
        

        # Course Appendix Slider
        self.course_appendix_label = ctk.CTkLabel(management_window, text="Append MHS = 7")
        self.course_appendix_label.pack(pady=(10, 0))
        self.course_appendix_slider = ctk.CTkSlider(management_window, from_=0, to=10, number_of_steps=10)
        self.course_appendix_slider.set(7)  # Default value
        self.course_appendix_slider.pack(pady=(0, 10))
        self.slider_value_label = ctk.CTkLabel(management_window, text="Slider Value: 1")
        self.slider_value_label.pack()
        self.update_slider_value_label()  # Start updating the label with the slider value
      
    def convert_csv(self, input_file):
        converted_data = []
        appendix_value = int(self.course_appendix_slider.get())  # Fetch the slider value
        with open(input_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Append the value to the course name
                course = row['Course'][appendix_value:].title()  # Adjust as per your requirements
                student = f"{row['First Name']} {row['Last Name']}".title()
                gender = row['Gender'].capitalize()
                grade = row['Grade']
                converted_data.append({'Course': course, 'Full Name': student, 'Gender': gender, 'Grade': grade, 'Check-in': []})
        return converted_data

    def save_csv(self, data):
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        folder_path = os.path.join(desktop_path, 'DataAT2')
        os.makedirs(folder_path, exist_ok=True)
        file_name = "converted_attendance_export.csv"
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Course", "Student", "Gender", "Grade", "Date", "Status"])
            for item in data:  # Assuming data is a list
                writer.writerow([item['Course'], item['Full Name'], item['Gender'], item['Grade'], '', ''])  # Adjust as needed
        return file_path

    def convert_to_json(self, data):
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
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        folder_path = os.path.join(desktop_path, 'DataAT2')
        os.makedirs(folder_path, exist_ok=True)
        file_name = "attendance_log.json"
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        return file_path

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            converted_data = self.convert_csv(file_path)
            saved_file_path_csv = self.save_csv(converted_data)
            json_data = self.convert_to_json(converted_data)
            saved_file_path_json = self.save_json(json_data)
            messagebox.showinfo("Conversion Successful", f"CSV file converted and saved to:\n{saved_file_path_csv}\n\nJSON file saved to:\n{saved_file_path_json}")

    def add_custom_class(self):
        new_class = self.add_class_entry.get().strip()
        if new_class and new_class not in self.classes:
            self.classes.append(new_class)
            self.class_selection.configure(values=self.classes)
            self.remove_class_dropdown.configure(values=self.classes)  # Update remove class
            messagebox.showinfo("Success", f"Class '{new_class}' added.")
            self.add_class_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Class already exists or field is empty.")

    def remove_class(self):
        class_to_remove = self.remove_class_selection.get()
        if class_to_remove in self.classes:
            # Update in-memory list and UI elements
            self.classes.remove(class_to_remove)
            self.class_selection.configure(values=self.classes)
            self.remove_class_dropdown.configure(values=self.classes)  # Update remove class dropdown
            messagebox.showinfo("Success", f"Class '{class_to_remove}' removed.")

            # Load the current JSON data
            file_path = self.get_data_file_path()
            with open(file_path, "r") as file:
                data = json.load(file)

            # Check if the class exists in the JSON data and remove it
            if class_to_remove in data:
                del data[class_to_remove]

                # Save the updated data back to the JSON file
                with open(file_path, "w") as file:
                    json.dump(data, file, indent=4)

                # Optional: Refresh the app or specific UI components to reflect changes
                self.refresh_app()
        else:
         messagebox.showwarning("Warning", "Please select a valid class to remove.")

    def export_data(self):
        file_path = self.get_data_file_path()
    
        self.generate_report(file_path, file_path.with_suffix('.txt'))
    
    def generate_report(self, file_path, output_file):
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
        audit_window = ctk.CTkToplevel(self)
        audit_window.title("Audit Log - Today's Check-Ins")
        audit_window.geometry("800x800")
        
                #Export Data Button
        export_button = ctk.CTkButton(audit_window, text="Export Data", command=self.export_data)
        export_button.pack(pady=(10, 0))

        result_area = scrolledtext.ScrolledText(audit_window, width=600, height=80)
        result_area.pack(pady=20)

        today = datetime.now().strftime("%Y-%m-%d")
        check_in_entries = []

    # Loop through all courses and students
        for course, students in self.attendance_data.items():
            for student, details in students.items():
                for record in details['Check-in']:
                    if record['Date'] == today:
                        time = record['Time']
                    # Append the entry within the if block to ensure 'time' is defined
                        check_in_entries.append((today, time, student, course))

    # Sort entries by date and time (most recent first)
        check_in_entries.sort(key=lambda entry: (entry[0], entry[1]), reverse=True)

    # Check if there are any check-in entries and display them
        if check_in_entries:
            for date, time, student, course in check_in_entries:
                result_area.insert('end', f"{student} ({course}) - {date} at {time}\n")
        else:
            result_area.insert('end', "No check-ins for today.")

    
        
def main():
    app = CheckInApp()
    app.mainloop()

if __name__ == "__main__":
    main()
