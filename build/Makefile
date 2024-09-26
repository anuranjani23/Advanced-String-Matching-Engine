# Makefile for compiling the string search algorithms

# Compiler to use
CXX := g++ 

# Compiler flags
CXXFLAGS := -O2 -std=c++14

# Targets
TARGETS := rabin_karp_search naive_search aho_corasick_search boyer_moore_search dfa_search

# Default target: build all executables
all: $(TARGETS)

# Rule to build rabin_karp_search executable
rabin_karp_search: src/rabin_karp_search.cpp
	$(CXX) $(CXXFLAGS) $< -o build/rabin_karp_search

# Rule to build naive_search executable
naive_search: src/naive_search.cpp
	$(CXX) $(CXXFLAGS) $< -o build/naive_search

# Rule to build aho_corasick_search executable
aho_corasick_search: src/aho_corasick_search.cpp
	$(CXX) $(CXXFLAGS) $< -o build/aho_corasick_search

# Rule to build boyer_moore_search executable
boyer_moore_search: src/boyer_moore_search.cpp
	$(CXX) $(CXXFLAGS) $< -o build/boyer_moore_search

# Rule to build dfa_search executable
dfa_search: src/dfa_search.cpp
	$(CXX) $(CXXFLAGS) $< -o build/dfa_search

# Clean target to remove executables
clean:
	rm -f build/*

# Phony targets to prevent conflicts with files of the same name
.PHONY: all clean
