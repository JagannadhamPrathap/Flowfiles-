from flask import Flask, request, send_from_directory, render_template
from pathlib import Path
import threading, time, os, uuid

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "shared_files"
UPLOAD_FOLDER.mkdir(exist_ok=True)
file_map = {}

@app.route("/", methods=["GET", "POST"])
def home():
    global file_map
    if request.method == "POST":
        file = request.files["file"]
        if file:
            file_ext = Path(file.filename).suffix
            unique_name = f"{uuid.uuid4().hex}{file_ext}" 
            filepath = UPLOAD_FOLDER / unique_name
            file.save(filepath)
            file_map[file.filename] = unique_name
    files = [{"original": orig, "unique": uniq} for orig, uniq in file_map.items()]
    return render_template("home.html", files=files)

@app.route("/download/<unique>")
def download(unique):
    return send_from_directory(UPLOAD_FOLDER, unique, as_attachment=True)

def cleanup_files():
    global file_map
    while True:
        time.sleep(60)
        now = time.time()
        for file in list(UPLOAD_FOLDER.iterdir()):
            try:
                if file.is_file():
                    if now - file.stat().st_mtime > 60:
                        os.remove(file)
                        for k, v in list(file_map.items()):
                            if v == file.name:
                                del file_map[k]
                        print(f"[CLEANUP] Removed {file.name}")
            except Exception as e:
                print(f"[ERROR] Failed to delete {file}: {e}")

threading.Thread(target=cleanup_files, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
