from flask import Flask, request, jsonify
from flask import render_template
import subprocess
import os

app = Flask(__name__)

#
ALLOWED_SCRIPTS = {"11", "24", "40", "48", "53"}
SCRIPT_DIR = "/opt/scripts"

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/scripts", methods=["GET"])
def list_scripts():
    # 
    return jsonify({
        "allowed": list(ALLOWED_SCRIPTS),
        "scripts": list(ALLOWED_SCRIPTS)
    })

@app.route("/run", methods=["GET"])
def run_script():
    script_name = request.args.get("script", "").strip()

    #ке
    if not script_name or script_name not in ALLOWED_SCRIPTS:
        return jsonify({
            "status": "error",
            "message": "Invalid or missing script name",
            "allowed": list(ALLOWED_SCRIPTS),
            "stderr": "Script name must be one of the allowed values",
        }), 400

    script_path = os.path.join(SCRIPT_DIR, f"{script_name}.sh")

    #
    real_dir = os.path.realpath(SCRIPT_DIR)
    real_path = os.path.realpath(script_path)
    if not real_path.startswith(real_dir):
        return jsonify({
            "status": "error",
            "message": "Forbidden path traversal attempt",
            "stderr": "Path validation failed",
        }), 403

    try:
        result = subprocess.run(
            [script_path],
            capture_output=True,
            text=True,
            timeout=60,  #емени
            check=False,
        )
    except subprocess.TimeoutExpired:
        return jsonify({
            "status": "error",
            "message": "Script timed out",
            "stderr": "Execution exceeded timeout",
            "returncode": -1,
        }), 504
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Failed to execute script",
            "stderr": str(e),
            "returncode": -2,
        }), 500

    lines = result.stdout.strip().splitlines()
    message = lines[0] if lines else ""
    #и
    output = result.stdout

    return jsonify({
        "status": "ok" if result.returncode == 0 else "error",
        "script": script_name,
        "message": message,
        "output": output,
        "stderr": result.stderr,
        "returncode": result.returncode,
    })

if __name__ == "__main__":
    #ене
    app.run(host="0.0.0.0", port=8000)
