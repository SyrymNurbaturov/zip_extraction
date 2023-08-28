import requests

url = "http://127.0.0.1:8000/copy-zip/"  # Замените на адрес вашего FastAPI сервера

file_path = "C:\\Users\\Syrym.Nurbaturov\\PycharmProjects\\zip.zip"  # Укажите путь к вашему ZIP файлу

with open(file_path, "rb") as f:
    files = {"file": (file_path.split("\\")[-1], f)}
    print(files)
    response = requests.post(url, files=files)

    if response.status_code == 200:
        data = response.json()
        print("Файл успешно скопирован")
        nested_zip_paths = data["nested_zip_paths"]
        if nested_zip_paths:
            print("Вложенные ZIP файлы найдены:")
            for path in nested_zip_paths:
                print(path)
        else:
            print("Вложенных ZIP файлов не найдено")
    else:
        print("Произошла ошибка при загрузке файла")
        print(response.text)
