# ->> Scroll to the bottom for the code specifics.
import os
from flask import Flask, render_template, request, redirect, flash
from werkzeug.utils import secure_filename
import subprocess
import time
import random
import requests
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)
app.secret_key = 'key8888'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['BUILD_FOLDER'] = 'bin'
app.config['MAX_CONTENT_LENGTH'] = 175 * 1024 * 1024  # 16 MB upload limit

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['BUILD_FOLDER'], exist_ok=True)

def fetch_url_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for failed requests

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'lxml')  # or 'html.parser' if you don't have 'lxml'

        # Remove scripts and style tags (optional, but often useful for text extraction)
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()

        # Extract text from the remaining HTML
        text = soup.get_text()

        # Clean up the text by removing leading/trailing whitespace and multiple newlines
        cleaned_text = ' '.join(text.split())

        return cleaned_text
    except requests.RequestException as e:
        flash(f"Error fetching URL: {e}")
        return None
    
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

def save_text_to_temp_file(text):
    temp_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_text.txt')
    with open(temp_filename, 'w', encoding='utf-8') as temp_file:
        temp_file.write(text)
    return temp_filename

def generate_random_pattern(text, length=5):
    start = random.randint(0, len(text) - length)
    return text[start:start + length]

def random_pattern_search(text):
    total_time = 0
    results = {}
    algorithms = ['naive_search', 'rabin_karp_search', 'kmp_search', 'boyer_moore_search', 'dfa_search', 'z_search']

    temp_file = save_text_to_temp_file(text)

    # Run each algorithm 100 times
    for _ in range(100):
        pattern = generate_random_pattern(text, random.randint(5, 15))
        results[pattern] = {}

        for algorithm in algorithms:
            executable = os.path.join(app.config['BUILD_FOLDER'], algorithm)
            try:
                start_time = time.time()
                proc = subprocess.run([executable, temp_file, pattern],
                                      capture_output=True, text=True, check=True)
                end_time = time.time()
                total_time += end_time - start_time
                output = proc.stdout.strip()

                if output:
                    # Ensure correct output format (handling invalid output more gracefully)
                    try:
                        # Try to parse the output as a list of integers
                        positions_str = output.split(":")[1].strip()  # Get the part after ':'
                        if positions_str:  # Only process if it's not empty
                            positions = [int(pos) for pos in positions_str.split() if pos.isdigit()]
                            results[pattern] = positions
                        else:
                            results[pattern] = []
                    except (IndexError, ValueError) as e:
                        # Handle parsing errors or unexpected output formats
                        flash(f"Unexpected output from {algorithm}: {output}")
                        results[pattern] = []  # Set to empty if there's an error
                else:
                    results[pattern] = []
            except subprocess.CalledProcessError as e:
                flash(f'Error running {algorithm} for pattern "{pattern}": {e.stderr}')
                results[pattern] = []
    
    return results, total_time / len(algorithms)


@app.route('/', methods=['GET', 'POST'])
def index():
    results = {}
    calc_time = 0
    search_method = ""
    patterns = ""
    uploaded_file = None
    algorithm_used = {}  

    if request.method == 'POST':
        if 'url' in request.form and request.form['url']:
            url = request.form['url']
            text_content = fetch_url_content(url)
            if text_content is None:
                return redirect(request.url)
            
            filepath = save_text_to_temp_file(text_content)
            
        elif 'textfile' in request.files and request.files['textfile'].filename != '':
            file = request.files['textfile']
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            uploaded_file = filename

            with open(filepath, 'r', encoding='utf-8') as f:
                text_content = f.read()
        else:
            flash('Please provide either a file or a URL.')
            return redirect(request.url)
        
        if 'random_pattern_search' in request.form:
            results, calc_time = random_pattern_search(text_content)

        else:
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
                    elif search_method == 'dfa':
                        search_method = 'dfa_search'
                        algorithm_used = 'Finite-Automata'
                    elif search_method == 'z':
                        search_method = 'z_search'
                        algorithm_used = 'Z-Algorithm'

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
                            flash(f'Error running {search_method} for pattern "{pattern}": {e.stderr}')
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
                    elif method == 'dfa':
                        method = 'dfa_search'
                        algorithm_used = 'Finite-Automata'
                    elif method == 'z':
                        method = 'z_search'
                        algorithm_used = 'Z-Algorithm'
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
                        flash(f'Error running {method} for pattern "{pattern}": {e.stderr}')
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
