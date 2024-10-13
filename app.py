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
    algorithm_used = {}  

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

        if 'use_selected_algorithm' in request.form:
            selected_algorithm = request.form.get('algorithm')
            if selected_algorithm and selected_algorithm != 'none':
                search_method = selected_algorithm  
                if search_method == 'naive':
                    search_method = 'naive_search'
                    algorithm_used = 'Naive'
                elif search_method == 'rabin':
                    search_method = 'rabin_karp_search'
                    algorithm_used = 'Rabin-Karp'
                elif search_method == 'boyer':
                    search_method = 'boyer_moore_search'
                    algorithm_used = 'Boyer-Moore'
                elif search_method == 'kmp':
                    search_method = 'kmp_search'
                    algorithm_used = 'KMP'

                executable = os.path.join(app.config['BUILD_FOLDER'], search_method)

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
                        flash(f'Error running {search_method} Search for pattern "{pattern}": {e.stderr}')
                        results[pattern] = []

        elif 'analyze_search' in request.form:
            results = {}
            search_method = "Auto-Analyzed"

            for pattern in patterns:
                method = analyze_search_method(pattern, text_content)
                if method == 'naive':
                    method = 'naive_search'
                    algorithm_used = 'Naive'
                elif method == 'rabin':
                    method = 'rabin_karp_search'
                    algorithm_used = 'Rabin-Karp'
                elif method == 'boyer':
                    method = 'boyer_moore_search'
                    algorithm_used = 'Boyer-Moore'
                elif method == 'kmp':
                    method = 'kmp_search'
                    algorithm_used = 'KMP'
                executable = os.path.join(app.config['BUILD_FOLDER'], method)

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
                    flash(f'Error running {method} Search for pattern "{pattern}": {e.stderr}')
                    results[pattern] = []

        return render_template('index.html', text=text_content, patterns=",".join(patterns), results=results, 
                               times=calc_time, algorithm=search_method, uploaded_file=uploaded_file, 
                               algorithm_used=algorithm_used)  
    # Pass the algorithm used in auto-analysis

    return render_template('index.html', results=results, times=calc_time, algorithm=search_method, 
                           patterns=patterns, algorithm_used=algorithm_used)

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

# analyze search method approach (for currently 4 algos)---> 
# Boyer-Moore is efficient for patterns with fewer unique chars.
# (KMP) is useful if the pattern has many repeating chars.
# Naive search for the small patterns and small text size (better overhead).
# RK works comparatively well when both pattern and text have many repeating chars.