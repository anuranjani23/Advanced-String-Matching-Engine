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
from typing import List
import math

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
    """
    Analyzes text and patterns to recommend the most suitable string searching algorithm.
    
    Args:
        text (str): The text to be searched
        patterns (List[str]): List of patterns to search for
    
    Returns:
        str: Name of the recommended search algorithm
    """
    if not text or not patterns:
        return "Naive"

    # Calculate text statistics
    text_length = len(text)
    text_unique_chars = len(set(text))
    
    # Calculate pattern statistics
    total_pattern_length = sum(len(p) for p in patterns)
    avg_pattern_length = total_pattern_length / len(patterns)
    max_pattern_length = max(len(p) for p in patterns)
    min_pattern_length = min(len(p) for p in patterns)
    all_pattern_chars = set(''.join(patterns))
    pattern_alphabet_size = len(all_pattern_chars)

    # Multiple patterns case
    if len(patterns) > 1:
        # For long patterns with small alphabet, Boyer-Moore is often faster
        # especially when patterns share suffixes
        if (avg_pattern_length > 20 and 
            pattern_alphabet_size < 30 and 
            max_pattern_length / min_pattern_length < 3):  # Patterns are of similar length
            return "Boyer-Moore"
            
        # Aho-Corasick is generally best for multiple patterns
        # but not when patterns are very long and text is relatively short
        if total_pattern_length > text_length * 0.1:
            return "Boyer-Moore"
        return "Aho-Corasick"

    # Single pattern analysis
    pattern = patterns[0]
    pattern_length = len(pattern)
    
    # Calculate character frequencies and entropy
    char_freq = {}
    for c in pattern:
        char_freq[c] = char_freq.get(c, 0) + 1
    
    entropy = 0
    for count in char_freq.values():
        prob = count / pattern_length
        entropy -= prob * math.log2(prob)
    
    # Calculate pattern characteristics
    first_char_freq = text.count(pattern[0]) / text_length if text_length > 0 else 0
    pattern_unique_chars = len(set(pattern))
    pattern_occurrences = text.count(pattern)
    
    # Check for pattern periodicity
    def is_periodic(p: str) -> bool:
        if len(p) <= 1:
            return False
        for i in range(1, len(p) // 2 + 1):
            if p[:i] * (len(p) // i) == p[:len(p) // i * i]:
                return True
        return False

    # Very short patterns or text - use naive approach
    if pattern_length <= 5 or text_length <= 100:
        return "Naive"
        
    # DFA is excellent for:
    # - Short to medium patterns that appear frequently
    # - Small alphabet size
    # - When the text will be searched multiple times
    if (pattern_length <= 30 and 
        pattern_alphabet_size <= 26 and
        pattern_occurrences > text_length / 1000):
        return "DFA"
    
    # KMP is good for:
    # - Periodic patterns
    # - Patterns with repeating prefixes
    # - When the pattern appears frequently
    if (is_periodic(pattern) or 
        pattern_occurrences > text_length / 100 or
        (pattern_length > 10 and pattern_unique_chars < pattern_length * 0.6)):
        return "KMP"
    
    # Boyer-Moore is excellent for:
    # - Long patterns
    # - Large alphabet size
    # - When the pattern is rare in the text
    if ((pattern_length > 15 and first_char_freq < 0.1) or
        (pattern_length > 20 and pattern_alphabet_size > 20) or
        (pattern_length > text_length * 0.01 and entropy > 3.0)):
        return "Boyer-Moore"
    
    # Rabin-Karp is good for:
    # - Short patterns with low entropy
    # - When looking for multiple patterns of the same length
    # - Patterns with many repeated characters
    if (entropy < 2.5 and pattern_length < 20) or pattern_unique_chars < pattern_length * 0.4:
        return "Rabin-Karp"
    
    # Z algorithm is good for:
    # - Medium length patterns
    # - When preprocessing the pattern is beneficial
    # - General-purpose cases where other algorithms don't have clear advantages
    if pattern_length > 10 and pattern_length <= 100:
        return "Z"
        
    # Default to Boyer-Moore for very long patterns
    if pattern_length > 100:
        return "Boyer-Moore"
        
    # For everything else, use KMP as a reliable default
    return "KMP"

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

def run_search_algorithm_aho_corasick(executable_path: str, input_file: str, patterns: List[str]) -> tuple[float, Dict[str, List[int]]]:
    try:
        start_time = time.time()
        proc = subprocess.run(
            [executable_path, input_file] + patterns,
            capture_output=True,
            text=True,
            check=True,
            timeout=30  # Add timeout
        )
        execution_time = time.time() - start_time
        
        output = proc.stdout.strip()
        positions_dict = {}
        
        # Parse output for each pattern
        if output:
            try:
                for line in output.split('\n'):
                    parts = line.split(":")
                    if len(parts) == 2:
                        pattern = parts[0].strip()
                        positions = list(map(int, parts[1].strip().split()))
                        positions_dict[pattern] = positions
            except (IndexError, ValueError) as e:
                logger.error(f"Error parsing Aho-Corasick algorithm output: {str(e)}")
                
        return execution_time, positions_dict
    except subprocess.TimeoutExpired:
        logger.error(f"Aho-Corasick algorithm execution timed out for patterns: {', '.join(patterns)}")
        return 0.0, {}
    except subprocess.CalledProcessError as e:
        logger.error(f"Aho-Corasick algorithm execution failed: {str(e)}")
        return 0.0, {}

@app.route('/')
def index():
    return render_template('index.html')

def run_search_algorithm_aho_corasick(executable_path: str, input_file: str, patterns: List[str]) -> tuple[float, Dict[str, List[int]]]:
    try:
        start_time = time.time()
        proc = subprocess.run(
            [executable_path, input_file] + patterns,
            capture_output=True,
            text=True,
            check=True,
            timeout=30  # Add timeout
        )
        execution_time = time.time() - start_time
        
        output = proc.stdout.strip()
        positions_dict = {}
        
        # Parse output for each pattern
        if output:
            try:
                for line in output.split('\n'):
                    parts = line.split(":")
                    if len(parts) == 2:
                        pattern = parts[0].strip()
                        positions = list(map(int, parts[1].strip().split()))
                        positions_dict[pattern] = positions
            except (IndexError, ValueError) as e:
                logger.error(f"Error parsing Aho-Corasick algorithm output: {str(e)}")
                
        return execution_time, positions_dict
    except subprocess.TimeoutExpired:
        logger.error(f"Aho-Corasick algorithm execution timed out for patterns: {', '.join(patterns)}")
        return 0.0, {}
    except subprocess.CalledProcessError as e:
        logger.error(f"Aho-Corasick algorithm execution failed: {str(e)}")
        return 0.0, {}

# Adjustments in the /search endpoint
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
            if algorithm == 'Aho-Corasick':
                execution_time, results = run_search_algorithm_aho_corasick(executable, filepath, patterns)
                calc_time = execution_time
            else:
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

# Adjustments in the /analyze endpoint
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
            
            if algo == "Aho-Corasick":
                execution_time, positions = run_search_algorithm_aho_corasick(executable, filepath, patterns)
                algo_time = execution_time
                if algo == best_algorithm:
                    results.update(positions)
            else:
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