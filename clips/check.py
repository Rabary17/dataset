import os

def delete_short_wav_files_by_size():
    directory = os.getcwd()
    if not os.path.isdir(directory):
        print(f"The directory '{directory}' does not exist.")
        return

    deleted_files_count = 0
    size_threshold = 16000 * 2 * 2  # 16,000 échantillons/seconde * 2 secondes * 2 octets/échantillon

    for filename in os.listdir(directory):
        if filename.endswith('.wav'):
            file_path = os.path.join(directory, filename)
            try:
                file_size = os.path.getsize(file_path)
                if file_size < size_threshold:
                    os.remove(file_path)
                    print(f"Deleted: {file_path} (size: {file_size} bytes)")
                    deleted_files_count += 1
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

    print(f"Total files deleted: {deleted_files_count}")

# Exemple d'utilisation
delete_short_wav_files_by_size()
