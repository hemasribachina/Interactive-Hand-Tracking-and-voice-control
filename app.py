from flask import Flask, render_template, jsonify
import subprocess
import os
import signal

app = Flask(__name__)

processes = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start/<script>')
def start_script(script):
    if script in processes and processes[script]:
        return jsonify({"message": f"{script} is already running!"})

    try:
        process = subprocess.Popen(["python", f"{script}.py"])
        processes[script] = process.pid
        return jsonify({"message": f"Started {script}!"})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/stop/<script>')
def stop_script(script):
    if script in processes and processes[script]:
        try:
            os.kill(processes[script], signal.SIGTERM)
            processes[script] = None
            return jsonify({"message": f"Stopped {script}!"})
        except Exception as e:
            return jsonify({"error": str(e)})
    return jsonify({"message": f"{script} is not running!"})

if __name__ == '__main__':
    app.run(debug=True)
