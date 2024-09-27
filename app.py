import os
from flask import Flask, render_template, request, redirect, flash
from werkzeug.utils import secure_filename
import subprocess
import time

app = Flask(__name__)
app.secret_key = 'key8888' 
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['BUILD_FOLDER'] = 'bin'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB upload limit

# Ensuring that the upload and build directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['BUILD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Initialize variables to avoid 'undefined' errors in the template
    results = {}
    calc_time = 0
    search_method = ""
    patterns = ""

    if request.method == 'POST':
        # Handle the file uploads
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

            # Reading the text content
            with open(filepath, 'r', encoding='utf-8') as f:
                text_content = f.read()

            # Handling the pattern input
            patterns = request.form.get('patterns', '')
            patterns = [p.strip() for p in patterns.split(',') if p.strip()]
            if not patterns:
                flash('No patterns provided')
                return redirect(request.url)

            # Determining which button was pressed
            search_method = None
            if 'naive' in request.form:
                search_method = 'Naive'
            elif 'rabin' in request.form:
                search_method = 'Rabin'

            results, calc_time = {}, 0
            if search_method == 'Naive':
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
                        positions = list(map(int, output.split(":")[1].split()))
                        results[pattern] = positions
                    else:
                        results[pattern] = []

                except subprocess.CalledProcessError as e:
                    flash(f'Error running Rabin-Karp: {e.stderr}')
                    for pat in patterns:
                        results[pat] = []

            return render_template('index.html', text=text_content, patterns=",".join(patterns), results=results, times=calc_time, algorithm=search_method)

    # Render the template for GET request or empty POST request
    return render_template('index.html', results=results, times=calc_time, algorithm=search_method, patterns=patterns)
