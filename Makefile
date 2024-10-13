# Makefile for compiling the string search algorithms

# Compiler to use
CXX := g++

# Compiler flags
CXXFLAGS := -O2 -std=c++14

# Targets
TARGETS := naive_search rabin_karp_search boyer_moore_search kmp_search

# Source files (assuming all source files are in the src/ directory)
SOURCES := $(patsubst %, src/%.cpp, $(TARGETS))

# Binary directory
BIN_DIR := bin

# Default target: build all executables
all: $(BIN_DIR) $(TARGETS)

# Create the bin directory if it doesn't exist
$(BIN_DIR):
	mkdir -p $(BIN_DIR)

# Pattern rule to build each target
$(TARGETS): %: src/%.cpp | $(BIN_DIR)
	$(CXX) $(CXXFLAGS) $< -o $(BIN_DIR)/$@

# Clean target to remove executables
clean:
	@rm -f $(BIN_DIR)/*

# Phony targets to prevent conflicts with files of the same name
.PHONY: all clean
