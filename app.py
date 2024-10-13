# ->> Scroll to the bottom for the code specifics.

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

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['BUILD_FOLDER'], exist_ok=True)

def analyze_search_method(pattern, text):
    m = len(pattern)
    n = len(text)

    if m == 0 or n == 0:
        return "naive" 

    unique_chars_pattern = len(set(pattern))
    unique_chars_text = len(set(text))

    
    if unique_chars_pattern <= m // 2:
        return "boyer"

    if text.count(pattern[0]) > (n // m) and unique_chars_pattern > m // 2:
        return "kmp"

    if m <= 10 and n <= 200: 
        return "naive"

    if unique_chars_pattern < m and unique_chars_text < n:
        return "rabin"
    
    return "kmp"
    
@app.route('/', methods=['GET', 'POST'])
def index():
    results = {}
    calc_time = 0
    search_method = ""
    patterns = ""
    uploaded_file = None

    if request.method == 'POST':
            if 'textfile' in request.files and request.files['textfile'].filename != '':
                file = request.files['textfile']
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_file = filename  
            elif 'uploaded_file' in request.form and request.form['uploaded_file'] != '':
                uploaded_file = request.form['uploaded_file']
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file)
            else:
                flash('No file uploaded or selected.')
                return redirect(request.url)

            
            with open(filepath, 'r', encoding='utf-8') as f:
                text_content = f.read()

            patterns = request.form.get('patterns', '')
            patterns = [p.strip() for p in patterns.split(',') if p.strip()]
            if not patterns:
                flash('No patterns provided')
                return redirect(request.url)

            search_method = None
            if 'naive' in request.form:
                search_method = 'Naive'
            elif 'rabin' in request.form:
                search_method = 'Rabin'
            elif 'boyer' in request.form:
                search_method = 'Boyer'

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

            elif search_method == 'Rabin':
                executable = os.path.join(app.config['BUILD_FOLDER'], 'rabin_karp_search')
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
                        flash(f'Error running Rabin-Karp Search for pattern "{pattern}": {e.stderr}')
                        results[pattern] = []

            elif search_method == 'Boyer':
                executable = os.path.join(app.config['BUILD_FOLDER'], 'boyer_moore_search')
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
                        flash(f'Error running Boyer-Moore Search for pattern "{pattern}": {e.stderr}')
                        results[pattern] = []

            return render_template('index.html', text=text_content, patterns=",".join(patterns), results=results, times=calc_time, 
                                   algorithm=search_method, uploaded_file=uploaded_file)

    return render_template('index.html', results=results, times=calc_time, algorithm=search_method, patterns=patterns)

if __name__ == "__main__":
    app.run(debug=True)

# Ensuring that the upload and build directories exist.
# Initialize variables to avoid 'undefined' errors in the template.
# Handle the file uploads.
# Reusing the previously uploaded files, if no new one is added.
# Reading the text content.
# Handling the pattern input.
# Determining which button was pressed.
# Render the template for GET request or empty POST request and retaining the uploaded file reference.


# analyze search method approach (for currently 4 algos)---> 
# Boyer-Moore is efficient for patterns with fewer unique chars.
# (KMP) is useful if the pattern has many repeating chars.
# Naive search for the small patterns and small text size (better overhead).
# RK works comparatively well when both pattern and text have many repeating chars.
