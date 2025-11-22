import json

def save_to_json(filename, students_dict):
    data = {"students": []}

    for name, student in students_dict.items():
        data["students"].append({
            "name": student.name,
            "grades": student.grades
        })

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Data successfully saved to {filename}")


def load_from_json(filename, StudentClass):
    try:
        with open(filename, "r") as f:
            data = json.load(f)

        students = {}

        # Expecting: {"students": [ {name:..., grades:...}, ... ]}
        students_list = data.get("students", [])

        for entry in students_list:
            name = entry.get("name")
            grades = entry.get("grades", [])
            
            if name:
                students[name] = StudentClass(name, grades)

        print(f"Data successfully loaded from {filename}")
        return students

    except FileNotFoundError:
        print("JSON file not found.")
        return None

    except json.JSONDecodeError:
        print("Error reading JSON file.")
        return None