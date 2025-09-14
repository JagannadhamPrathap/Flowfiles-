from flask import Flask, request, render_template_string, redirect, url_for
from pathlib import Path
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Upload folder inside project
upload_folder = Path(__file__).resolve().parent / "uploads"
upload_folder.mkdir(exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def upload():
    message = ""
    if request.method == "POST":
        file = request.files["file"]  # Get file from form
        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = upload_folder / filename
            file.save(filepath)
            message = f"✅ Uploaded: {filename}"
        else:
            message = "⚠️ No file selected"

    # Generate files list dynamically
    files = [f.name for f in upload_folder.iterdir() if f.is_file()]

    return render_template_string("""
        <script src='https://cdn.tailwindcss.com'></script>
        <div class="p-6 bg-white rounded-xl shadow-md w-full max-w-md mx-auto">
            <h2 class="text-xl font-bold mb-4 text-center text-blue-600">📂 Upload File</h2>

            {% if message %}
                <p class="text-green-600 font-medium mb-4">{{ message }}</p>
            {% endif %}

            <form method="POST" enctype="multipart/form-data" class="space-y-4">
                <input type="file" name="file"
                    class="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <input type="submit" value="Upload"
                    class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg shadow-md transition">
            </form>

            {% if files %}
                <h3 class="text-lg font-semibold mt-6 mb-2">Uploaded Files:</h3>
                <ul class="list-disc pl-5 space-y-1">
                    {% for f in files %}
                        <li class="flex justify-between items-center">
                            <span>{{ f }}</span>
                            <a href="{{ url_for('delete_file', filename=f) }}"
                               class="text-red-600 hover:text-red-800 text-sm">Delete</a>
                        </li>
                    {% endfor %}
                </ul>
            {% endif %}
        </div>
    """, message=message, files=files)

@app.route('/delete/<filename>')
def delete_file(filename):
    filename = secure_filename(filename)
    filepath = upload_folder / filename
    if filepath.exists() and filepath.is_file():
        filepath.unlink()
    return redirect(url_for('upload'))

if __name__ == "__main__":
    app.run(port=5000, debug=True)