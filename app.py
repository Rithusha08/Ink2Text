
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_file = request.files["pdf"]
        if uploaded_file and uploaded_file.filename.endswith(".pdf"):
            filename = secure_filename(uploaded_file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            uploaded_file.save(filepath)

            doc = fitz.open(filepath)
            full_text = ""

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                text = pytesseract.image_to_string(img)
                full_text += f"\n--- Page {page_num + 1} ---\n" + text + "\n"

            output_text_file = os.path.join(OUTPUT_FOLDER, filename.replace(".pdf", ".txt"))
            with open(output_text_file, "w", encoding="utf-8") as f:
                f.write(full_text)

            return send_file(output_text_file, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
