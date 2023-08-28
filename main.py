from fastapi import FastAPI, UploadFile, File
import os
import uvicorn
import zipfile
import shutil
import re
import patoolib
import subprocess
from pathlib import Path
app = FastAPI()

# Путь к директории, в которую будет скопирован ZIP файл
target_directory = "..\\storage"


def fix_filename(filename):
    # Replace special characters and spaces with underscores
    return re.sub(r'[^\w\d.-]', '', filename)

def extract_and_cleanup_nested_archives(archive_path, extract_to_dir):
    # Create a directory for extraction
    os.makedirs(extract_to_dir, exist_ok=True)

    archive_extension = os.path.splitext(archive_path)[1]

    if archive_extension == ".zip":
        with zipfile.ZipFile(archive_path, 'r') as main_archive:
            main_archive.extractall(extract_to_dir)

    nested_archive_paths = []
    for root, _, files in os.walk(extract_to_dir):
        for file in files:
            if file.endswith(".zip") or file.endswith(".rar"):
                nested_archive_paths.append(os.path.join(root, file))

    for nested_archive_path in nested_archive_paths:
        extract_nested_archive(nested_archive_path, extract_to_dir)

    archive_name = extract_to_dir + "_copy"
    shutil.make_archive(archive_name, "zip", extract_to_dir)

    archive_size = os.path.getsize(archive_path)
    copy_archive_size = os.path.getsize(archive_name + ".zip")

    # Convert sizes to megabytes
    archive_size_mb = archive_size / (1024 * 1024)
    copy_archive_size_mb = copy_archive_size / (1024 * 1024)

    shutil.rmtree(extract_to_dir)

    size_info = {
        "archive_name": os.path.basename(archive_path),
        "archive_size_mb": archive_size_mb,
        "copy_archive_name": os.path.basename(archive_name + ".zip"),
        "copy_archive_size_mb": copy_archive_size_mb
    }

    return size_info


def extract_nested_archive(nested_archive_path, extract_dir):
    nested_archive_name = os.path.basename(nested_archive_path)

    if re.match(r".*\.zip$", nested_archive_name):
        nested_archive_name = nested_archive_name.replace(" ", "_")

    nested_extract_to_dir = os.path.join(
        os.path.dirname(nested_archive_path), os.path.splitext(nested_archive_name)[0]
    )

    Path(nested_extract_to_dir).mkdir(parents=True, exist_ok=True)

    try:
        print(f"Extracting {nested_archive_path} to {nested_extract_to_dir}")
        patoolib.extract_archive(nested_archive_path, outdir=nested_extract_to_dir)
    except Exception as e:
        print(f"Error extracting {nested_archive_path}: {e}")

    os.remove(nested_archive_path)

    for root, _, files in os.walk(nested_extract_to_dir):
        for file in files:
            if file.endswith(".zip") or file.endswith(".rar"):
                extract_nested_archive(os.path.join(root, file), nested_extract_to_dir)


@app.post("/copy-zip/")
def copy_zip_file(file: UploadFile = File(...)):
    file_path = os.path.join(target_directory, file.filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    nested_zip_paths = []

    with zipfile.ZipFile(file_path, "r") as zip_ref:
        for file_info in zip_ref.infolist():
            if file_info.filename.endswith(".zip"):
                nested_zip_paths.append(file_info.filename)

    return {"message": "Файл успешно скопирован", "nested_zip_paths": nested_zip_paths}

@app.post("/extract_zips/")
def extract_zips(file: UploadFile = File(...)):
    zip_path = os.path.abspath(os.path.join(target_directory, file.filename))
    zip_name = os.path.splitext(file.filename)[0]
    zip_name = fix_filename(zip_name)  # Fix the filename if needed
    extract_to_dir = os.path.join(target_directory, zip_name)

    sizes = extract_and_cleanup_nested_archives(zip_path, extract_to_dir)

    return {"message": "Внутренние ZIP файлы успешно обработаны", "sizes": sizes}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
