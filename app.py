import os
from flask import Flask, render_template, request, redirect, flash
from werkzeug.utils import secure_filename
import subprocess
import time

app = Flask(__name__)
app.secret_key = 'key8888' 
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['BUILD_FOLDER'] = 'build'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB upload limit

# Ensure upload and build directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['BUILD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle file upload
        if 'textfile' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['textfile']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Read the text content
            with open(filepath, 'r', encoding='utf-8') as f:
                text_content = f.read()

            # Handle pattern input
            patterns = request.form.get('patterns', '')
            patterns = [p.strip() for p in patterns.split(',') if p.strip()]
            if not patterns:
                flash('No patterns provided')
                return redirect(request.url)

            # Determine which button was pressed
            search_method = None
            if 'naive' in request.form:
                search_method = 'naive'
            elif 'rabin' in request.form:
                search_method = 'rabin'

            results, calc_time = {}, 0
            if search_method == 'naive':
                executable = os.path.join(app.config['BUILD_FOLDER'], 'naive_search')
                for pattern in patterns:
                    try:
                        start_time = time.time()
                        proc = subprocess.run([executable, filepath, pattern],
                                              capture_output=True, text=True, check=True)
                        end_time = time.time()
                        calc_time += end_time - start_time
                        output = proc.stdout.strip()
                        if output:
                            positions = list(map(int, output.split(":")[1].split()))
                            results[pattern] = positions
                        else:
                            results[pattern] = []
                    except subprocess.CalledProcessError as e:
                        flash(f'Error running Naive Search for pattern "{pattern}": {e.stderr}')
                        results[pattern] = []
                
            elif search_method == 'rabin':
                executable = os.path.join(app.config['BUILD_FOLDER'], 'rabin_karp_search')
                patterns_str = ','.join(patterns)
                try:
                    start_time = time.time()
                    proc = subprocess.run([executable, filepath, patterns_str],
                                          capture_output=True, text=True, check=True)
                    end_time = time.time()
                    calc_time = end_time - start_time
                    output = proc.stdout.strip()
                    if output:
                        for line in output.split('\n'):
                            print(line)
                            pat, pos_str = line.split(':')
                            positions = list(map(int, pos_str.strip().split()))
                            results[pat] = positions
                    else:
                        for pat in patterns:
                            results[pat] = []
                except subprocess.CalledProcessError as e:
                    flash(f'Error running Rabin-Karp: {e.stderr}')
                    for pat in patterns:
                        results[pat] = []

            return render_template('index.html', text=text_content, patterns=",".join(patterns), results=results, times=calc_time, algorithm=search_method.upper())

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
