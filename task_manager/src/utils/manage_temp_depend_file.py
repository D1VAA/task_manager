import json
def save_depend_at_temp_file(task_local_id: int, task_depend_id: int):
    json_data = {}
    with open('dependencies.json', 'r') as file:
        # Tenta ler o arquivo caso exista.
        try: 
            json_data = json.load(file)
        except json.JSONDecodeError:
            json_data = {task_local_id: list()}
    if len(json_data) == 0:
        json_data[task_local_id] = list()
    json_data[task_local_id].append(task_depend_id)
    with open('dependencies.json', 'w') as file:
        json.dump(json_data, file, indent=4)

def get_all_depends():
    """
    Função para ler o arquivo com as dependências salvas.
    
    Returns:
        Dict[str, List[str]]: Retorna um dicionário com o ID da task na database e o ID da database da task que está relacionada.
    """
    try:
        with open('dependencies.json', 'r') as file:
            try:
                json_data = json.load(file)
            except json.JSONDecodeError:
                print("No dependencies found.")
                return {}
        return json_data
    except FileNotFoundError:
        json_data = {}
        with open('dependencies.json', 'w') as file:
            json.dump(json_data, file, indent=4)
        return json_data
