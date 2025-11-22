import json

def save_to_json(filename, students):
    data = {}

    for name, student in students.items():
        data[name] = {
            "grades": student.grades
        }

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Data successfully saved to {filename}")


def load_from_json(filename, StudentClass):
    try:
        with open(filename, "r") as f:
            data = json.load(f)

        students = {}

        for name, info in data.items():
            s = StudentClass(name, info.get("grades", []))
            students[name] = s

        print(f"Data successfully loaded from {filename}")
        return students

    except FileNotFoundError:
        print("JSON file not found.")
        return None

    except json.JSONDecodeError:
        print("Error reading JSON file.")
        return None
