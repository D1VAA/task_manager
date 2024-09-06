import json
def save_depend_at_temp_file(task_local_id: int, task_depend_ids: list):
    try:
        with open('dependencies.json', 'w+') as file:
            # Tenta ler o arquivo caso exista.
            try: 
                json_data = json.load(file)
            except json.JSONDecodeError:
                print("JsonDecodeError")
                json_data = {}
            json_data[task_local_id] = task_depend_ids
            file.seek(0)
            file.truncate()

            json.dump(json_data, file, indent=4)
    except FileNotFoundError:
        print("JsonDecodeError")
        with open('dependencies.json', 'w') as file:
            json_data = {task_local_id: task_depend_ids}
            json.dump(json_data, file, indent=4)

def get_all_depends():
    with open('dependencies.json', 'r') as file:
        try:
            json_data = json.load(file)
        except json.JSONDecodeError:
            print("No dependencies found.")
            return
    return json_data