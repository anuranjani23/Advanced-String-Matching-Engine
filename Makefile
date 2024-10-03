# Makefile for compiling the string search algorithms

# Compiler to use
CXX := g++

# Compiler flags
CXXFLAGS := -O2 -std=c++14

# Targets
TARGETS := naive_search rabin_karp_search boyer_moore_search

# Default target: build all executables
all: bin $(TARGETS)

# Create the bin directory if it doesn't exist
bin:
	mkdir -p bin

# Rule to build naive_search executable
naive_search: src/naive_search.cpp | bin
	$(CXX) $(CXXFLAGS) $< -o bin/naive_search

# Rule to build rabin_karp_search executable
rabin_karp_search: src/rabin_karp_search.cpp | bin
	$(CXX) $(CXXFLAGS) $< -o bin/rabin_karp_search

# Rule to build boyer_moore_search executable
boyer_moore_search: src/boyer_moore_search.cpp | bin
	$(CXX) $(CXXFLAGS) $< -o bin/boyer_moore_search

# Clean target to remove executables
clean:
	rm -f bin/*

# Phony targets to prevent conflicts with files of the same name
.PHONY: all clean
