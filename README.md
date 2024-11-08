# Pattern Search Analysis Tool

This project is a web-based tool for analyzing the performance of different pattern search algorithms on a given text file. It allows users to upload a text file, enter one or multiple patterns, and perform searches using various algorithms. Users can choose to auto-select the optimal algorithm based on pattern characteristics, manually select an algorithm, or conduct a randomized pattern search analysis to compare algorithm performance.

## Features

- **File Upload**: Upload a text file to analyze.
- **Multiple Pattern Search**: Enter multiple patterns (comma-separated) for searching.
- **Auto-Analyze**: Automatically select the best algorithm based on pattern characteristics.
- **Manual Selection**: Choose an algorithm manually from Naive, Aho-Corasick, Boyer-Moore, KMP, Rabin-Karp, etc.
- **Random Pattern Analysis**: Generate random patterns to analyze algorithm performance across multiple runs.
- **Performance Comparison Chart**: Visualize the average time taken by each algorithm in random pattern analysis.

## Technologies Used

- **Front-End**: HTML, JavaScript, Bootstrap, Chart.js
- **Back-End**: Python (Flask)
- **Algorithms**: Implemented in C++ (Naive, Boyer-Moore, KMP, Rabin-Karp, Aho-Corasick, Finite-Automata, Z-Algorithm)

## Pre-Requisites

- **Python 3.x** and **Flask**
- **C++ Compiler** to compile the algorithm binaries
- **Make** for building C++ binaries


## Installation and Setup

1. **Clone the Repository**

   ```bash
   git clone https://github.com/anuranjani23/pattern-search-analysis-tool.git
   cd pattern-search-analysis-tool
   ```

2. **Compile the Algorithm Binaries**

   Navigate to the root directory and run the `make` command to compile the C++ files in the `src/` directory and create binaries in the `bin/` folder.

   ```bash
   make
   ```

   This will generate the binaries `naive_search`, `boyer_moore_search`, `kmp_search`, and `rabin_karp_search`, `aho_corasick_search`, `z_search`, `dfa_search` in the `bin/` directory.

3. **Install Python Dependencies**

   Install Flask and any other required dependencies using `pip`.

   ```bash
   pip install flask
   pip install werkzeug
   pip install requests
   pip install beautifulsoup4
   pip install lxml
   ```

4. **Run the Flask Server**

   Start the Flask server on port 5000.

   ```bash
   python app.py
   ```

   The application will be accessible at `http://127.0.0.1:5000/`.

## Project Structure

```plaintext
.
├── bin/                 # Contains compiled binaries for the search algorithms
├── src/                 # C++ source code files for each search algorithm
│   ├── naive_search.cpp
│   ├── rabin_karp_search.cpp
│   ├── kmp_search.cpp
│   ├── boyer_moore_search.cpp
│   ├── dfa_search.cpp
│   ├── z_search.cpp
│   └── aho_corasick_search.cpp
├── templates/           # HTML template files for the Flask application
│   └── index.html       # Main front-end interface
├── uploads/             # Text files to search from
│   └── sample.txt       
├── app.py               # Flask server and application logic
├── Makefile             # Makefile to compile C++ binaries
├── README.md            # Project documentation
└── .gitignore           
```
## Usage

1. **Upload a Text File or a URL**

   Start by uploading a text file through the "Choose File" button. Or enter a URL.

2. **Enter Patterns**

   Enter one or more patterns in the provided text area, separated by commas.

3. **Choose Search Options**

   - **Auto-Analyze Search**: Automatically chooses the best algorithm based on the characteristics of each pattern.
   - **Manual Selection**: Allows you to select a specific algorithm from the dropdown and perform the search manually.
   - **Random Pattern Analysis**: Generates random patterns and evaluates each algorithm’s performance over multiple runs, displaying the results in a bar chart.

4. **View Results**

   Results are displayed in the "Results" section, and performance data is visualized in a bar chart when performing random pattern analysis.


## License

This project is licensed under the MIT License.