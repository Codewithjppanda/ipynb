from flask import Flask, request, send_file, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure upload settings - use /tmp for Vercel
UPLOAD_FOLDER = "/app/uploads"
OUTPUT_FOLDER = "/app/outputs"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/convert", methods=["POST"])
def convert_ipynb_to_pdf():
    try:
        if "file" not in request.files:
            logger.error("No file part in request")
            return jsonify({"error": "No file part"}), 400
        
        file = request.files["file"]
        if file.filename == "":
            logger.error("No selected file")
            return jsonify({"error": "No selected file"}), 400
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logger.info(f"Saving file to: {file_path}")
        file.save(file_path)

        # Expected output PDF filename
        output_pdf = os.path.join(app.config['OUTPUT_FOLDER'], f"{os.path.splitext(filename)[0]}.pdf")
        logger.info(f"Output PDF will be generated at: {output_pdf}")

        try:
            # Run nbconvert without executing the notebook (--no-input prevents execution)
            result = subprocess.run([
                "jupyter-nbconvert",
                "--to", "pdf",
                "--TemplateExporter.exclude_input=False",
                "--no-input",
                file_path,
                "--output-dir", app.config['OUTPUT_FOLDER']
            ], check=True, capture_output=True, text=True)
            
            logger.info("Conversion completed successfully")
            logger.info(result.stdout)
            
            if not os.path.exists(output_pdf):
                logger.error(f"Output PDF not found at: {output_pdf}")
                return jsonify({"error": "PDF file not generated"}), 500
            
            return send_file(
                output_pdf,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"{os.path.splitext(filename)[0]}.pdf"
            )
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Conversion failed with return code: {e.returncode}")
            logger.error(f"Error output: {e.stderr}")
            return jsonify({
                "error": "Conversion failed",
                "details": str(e),
                "stderr": e.stderr
            }), 500
        
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        return jsonify({"error": "Server error", "details": str(e)}), 500