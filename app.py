from flask import Flask, render_template, request, jsonify, flash
from werkzeug.utils import secure_filename
import os
import subprocess
import time
import random
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

@dataclass
class PatternMetrics:
    length: int
    occurrences: int
    avg_time: float
    min_time: float
    max_time: float
    std_dev: float

@dataclass
class AlgorithmPerformance:
    name: str
    display_name: str
    pattern_metrics: Dict[int, PatternMetrics]
    overall_avg_time: float
    total_patterns_tested: int
    total_matches: int

# Algorithm name mappings
ALGORITHM_EXECUTABLES = {
    'Naive': 'naive_search',
    'Rabin-Karp': 'rabin_karp_search',
    'KMP': 'kmp_search',
    'Boyer-Moore': 'boyer_moore_search',
    'DFA': 'dfa_search',
    'Z': 'z_search',
    'Aho-Corasick': 'aho_corasick_search'
}

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'key8888')  # Better to use environment variable
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['BUILD_FOLDER'] = 'bin'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['BUILD_FOLDER'], exist_ok=True)

def fetch_url_content(url: str) -> Optional[str]:
    try:
        response = requests.get(url, timeout=10)  
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        for element in soup(['script', 'style', 'header', 'footer', 'nav']):
            element.decompose()
        text = soup.get_text()
        return ' '.join(text.split())
    except requests.RequestException as e:
        logger.error(f"Error fetching URL {url}: {str(e)}")
        flash(f"Error fetching URL: {str(e)}")
        return None

def save_text_to_temp_file(text: str) -> str:
    temp_filename = os.path.join(app.config['UPLOAD_FOLDER'], f'temp_text_{int(time.time())}.txt')
    try:
        with open(temp_filename, 'w', encoding='utf-8') as temp_file:
            temp_file.write(text)
        return temp_filename
    except IOError as e:
        logger.error(f"Error saving temporary file: {str(e)}")
        raise

def analyze_search_method(text: str, patterns: List[str]) -> str:
    if not text or not patterns:
        return "Naive"

    # Multiple patterns case
    if len(patterns) > 1:
        return "Aho-Corasick"

    pattern = patterns[0]
    text_stats = {
        'length': len(text),
        'unique_chars': len(set(text)),
        'pattern_length': len(pattern),
        'pattern_unique_chars': len(set(pattern)),
        'pattern_frequency': text.count(pattern[0]) if pattern else 0
    }

    # Algorithm selection logic
    if text_stats['pattern_length'] <= 10 and text_stats['length'] <= 200:
        return "Naive"
    if text_stats['pattern_length'] > text_stats['length'] * 0.1:
        return "Boyer-Moore"
    if text_stats['pattern_frequency'] > (text_stats['length'] // text_stats['pattern_length']):
        return "KMP"
    if text_stats['pattern_unique_chars'] < text_stats['pattern_length'] * 0.5:
        return "Rabin-Karp"
    return "Z"

def generate_smart_patterns(text: str) -> List[str]:
    num_patterns = 5
    patterns = set()
    
    # Common words strategy
    words = [word for word in text.split() if len(word) >= 4]
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:2]
    patterns.update(word for word, _ in common_words)
    
    # Random substrings strategy
    lengths = [5, 10, 15]
    for length in lengths:
        if len(text) >= length:
            start = random.randint(0, len(text) - length)
            patterns.add(text[start:start + length])
    
    return list(patterns)[:num_patterns]

def run_search_algorithm(executable_path: str, input_file: str, pattern: str) -> tuple[float, List[int]]:
    try:
        start_time = time.time()
        proc = subprocess.run(
            [executable_path, input_file, pattern],
            capture_output=True,
            text=True,
            check=True,
            timeout=30  # Add timeout
        )
        execution_time = time.time() - start_time
        
        output = proc.stdout.strip()
        positions = []
        if output:
            try:
                positions = list(map(int, output.split(":")[1].split()))
            except (IndexError, ValueError) as e:
                logger.error(f"Error parsing algorithm output: {str(e)}")
                
        return execution_time, positions
    except subprocess.TimeoutExpired:
        logger.error(f"Algorithm execution timed out for pattern: {pattern}")
        return 0.0, []
    except subprocess.CalledProcessError as e:
        logger.error(f"Algorithm execution failed: {str(e)}")
        return 0.0, []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        # Input handling
        if 'url' in request.form and request.form['url']:
            text_content = fetch_url_content(request.form['url'])
            if text_content is None:
                return jsonify({'error': 'Failed to fetch URL content'}), 400
            filepath = save_text_to_temp_file(text_content)
        elif 'textfile' in request.files and request.files['textfile'].filename:
            file = request.files['textfile']
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                text_content = f.read()
        else:
            return jsonify({'error': 'No input provided'}), 400

        patterns = [p.strip() for p in request.form.get('patterns', '').split(',') if p.strip()]
        if not patterns:
            return jsonify({'error': 'No patterns provided'}), 400

        algorithm = request.form.get('algorithm', 'none')
        if algorithm not in ALGORITHM_EXECUTABLES:
            return jsonify({'error': 'Invalid algorithm specified'}), 400

        results = {}
        calc_time = 0
        
        if algorithm != 'none':
            executable = os.path.join(app.config['BUILD_FOLDER'], ALGORITHM_EXECUTABLES[algorithm])
            for pattern in patterns:
                execution_time, positions = run_search_algorithm(executable, filepath, pattern)
                calc_time += execution_time
                results[pattern] = positions

        return jsonify({
            'results': results,
            'times': round(calc_time, 7),
            'text_content': text_content[:1000],
            'algorithm_used': algorithm
        })

    except Exception as e:
        logger.error(f"Error in search endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Input handling
        if 'url' in request.form and request.form['url']:
            text_content = fetch_url_content(request.form['url'])
            if text_content is None:
                return jsonify({'error': 'Failed to fetch URL content'}), 400
            filepath = save_text_to_temp_file(text_content)
        elif 'textfile' in request.files and request.files['textfile'].filename:
            file = request.files['textfile']
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                text_content = f.read()
        else:
            return jsonify({'error': 'No input provided'}), 400

        patterns = [p.strip() for p in request.form.get('patterns', '').split(',') if p.strip()]
        if not patterns:
            return jsonify({'error': 'No patterns provided'}), 400

        best_algorithm = analyze_search_method(text_content, patterns)
        results = {}
        performance_data = {}

        for algo in ALGORITHM_EXECUTABLES:
            executable = os.path.join(app.config['BUILD_FOLDER'], ALGORITHM_EXECUTABLES[algo])
            algo_time = 0
            
            for pattern in patterns:
                execution_time, positions = run_search_algorithm(executable, filepath, pattern)
                algo_time += execution_time
                
                if algo == best_algorithm:
                    results[pattern] = positions
                        
            performance_data[algo] = algo_time

        return jsonify({
            'results': results,
            'times': round(performance_data[best_algorithm], 7),
            'text_content': text_content[:1000],
            'algorithm_used': best_algorithm,
            'performance': performance_data
        })

    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/random_analysis', methods=['POST'])
def random_analysis():
    try:
        if 'url' in request.form and request.form['url']:
            text_content = fetch_url_content(request.form['url'])
            if text_content is None:
                return jsonify({'error': 'Failed to fetch URL content'}), 400
        elif 'textfile' in request.files and request.files['textfile'].filename:
            file = request.files['textfile']
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                text_content = f.read()
        else:
            return jsonify({'error': 'No input provided'}), 400

        patterns = generate_smart_patterns(text_content)
        filepath = save_text_to_temp_file(text_content)
        
        performance_data = {}
        
        for algo in ALGORITHM_EXECUTABLES:
            executable = os.path.join(app.config['BUILD_FOLDER'], ALGORITHM_EXECUTABLES[algo])
            algo_time = 0
            
            for pattern in patterns:
                execution_time, _ = run_search_algorithm(executable, filepath, pattern)
                algo_time += execution_time
                
            performance_data[algo] = algo_time

        return jsonify({
            'performance': performance_data,
            'patterns_tested': patterns
        })

    except Exception as e:
        logger.error(f"Error in random_analysis endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == "__main__":
    app.run(debug=False)  # Set debug=False for production