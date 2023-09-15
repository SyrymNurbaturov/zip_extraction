import requests

url = "http://127.0.0.1:8000/extract_zips/"  # Замените на адрес вашего FastAPI сервера

file_path = "..\\storage\\cv3.0.zip"

with open(file_path, "rb") as f:
    files = {"file": (file_path.split("\\")[-1], f)}
    response = requests.post(url, files=files)

if response.status_code == 200:
    print("Внутренние ZIP файлы успешно обработаны")
    data = response.json()
    zip_name = data["sizes"]["archive_name"]
    zip_size_mb = data["sizes"]["archive_size_mb"]
    copy_zip_name = data["sizes"]["copy_archive_name"]
    copy_zip_size_mb = data["sizes"]["copy_archive_size_mb"]
    
    print(f"Имя зип файла {zip_name}, Размер: {zip_size_mb:.2f} MB")
    print(f"Имя копия зип файла {copy_zip_name}, Размер: {copy_zip_size_mb:.2f} MB")
else:
    print("Произошла ошибка при обработке внутренних ZIP файлов")
    print(response.text)
