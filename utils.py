def search_students(query, students_dict):
    query = query.lower()
    results = []

    for name in students_dict:
        if query in name.lower():
            results.append(name)

    return results
