CSV Entries must be :
State Code,Course,Room,Term(s),Last Name,First Name,Middle Name,Suffix,Alias,Gender,Grade,Start Date,End Date
The Converter looks for Course, Last Name, First Name, and Gender

The Application creates a folder on the desktop named DataAT2, This is where all the files and export will be stored

JSON is 

"Example Class": {
        "Test Student": {
            "Check-in": [
                {
                    "Date": "2024-03-13",
                    "Time": "11:33:24"
                },
                {
                    "Date": "2024-03-13",
                    "Time": "11:33:26"
                }
            ]
        }
    }

    python -m  PyInstaller AAT.py --onefile --noconsole
