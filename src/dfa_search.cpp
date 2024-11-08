// ->> Scroll to the bottom for the code and algorithm specifics.

#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <algorithm>

using namespace std;

#define num_of_char 256  

class OccurrenceFinder
{
private:
    string text;

    void constructDFA(const string &pattern, vector<vector<int>> &dfa, bool caseInsensitive) {
        int M = pattern.length();
        int x = 0;

        dfa.assign(M + 1, vector<int>(num_of_char, 0));

        if (caseInsensitive) {
            dfa[0][tolower(pattern[0])] = 1;
        } else {
            dfa[0][pattern[0]] = 1;
        }

        for (int j = 1; j < M; ++j) {
            for (int c = 0; c < num_of_char; ++c)
                dfa[j][c] = dfa[x][c];

            if (caseInsensitive) {
                dfa[j][tolower(pattern[j])] = j + 1;
            } else {
                dfa[j][pattern[j]] = j + 1;
            }

            x = dfa[x][pattern[j]];
        }

        for (int c = 0; c < num_of_char; ++c)
            dfa[M][c] = dfa[x][c];
    }

    vector<int> search(const string &pattern, bool caseInsensitive)
    {
        vector<int> occurrence;
        int M = pattern.length();
        int N = text.length();

        if (caseInsensitive)
        {
            string lowerText = text;
            transform(lowerText.begin(), lowerText.end(), lowerText.begin(), ::tolower);
            text = lowerText;
        }

        vector<vector<int>> dfa;
        constructDFA(pattern, dfa, caseInsensitive);

        int state = 0;

        for (int i = 0; i < N; i++)
        {
            state = dfa[state][text[i]];
            if (state == M)
            {
                occurrence.push_back(i - M + 1);
            }
        }

        return occurrence;
    }

public:
    OccurrenceFinder(const string &filename)
    {
        ifstream fileIn(filename);
        if (!fileIn.is_open())
        {
            cerr << "Error in opening file: " << filename << endl;
            exit(EXIT_FAILURE);
        }

        text.assign((istreambuf_iterator<char>(fileIn)), istreambuf_iterator<char>());
        fileIn.close();
    }

    void display_output(const string &pattern, const vector<int> &occurrences)
    {
        cout << pattern << ": ";
        if (occurrences.empty())
        {
            cout << endl; 
        }
        else
        {
            for (int index : occurrences)
            {
                cout << " " << index;
            }
            cout << endl; 
        }
    }

    void findOccurrences(const string &pattern, bool caseInsensitive = false)
    {
        vector<int> occurrences = search(pattern, caseInsensitive);
        display_output(pattern, occurrences);
    }
};

int main(int argc, char *argv[])
{
    if (argc < 3)
    {
        cerr << "Usage: " << argv[0] << " <filename> <pattern> [--case-insensitive]" << endl;
        return 1;
    }

    string filename = argv[1];
    string pattern = argv[2];
    bool caseInsensitive = (argc == 4 && string(argv[3]) == "--case-insensitive");

    OccurrenceFinder finder(filename);
    finder.findOccurrences(pattern, caseInsensitive);

    return 0;
}

/* After creating the automaton, the text is fed to this automaton char by char and it will change its state based on that, when it changes to the final state
we will accept that char and print the first occurrence of the pattern as at this point we have already found our pattern in the prefix read.*/

/* Now automaton (a directed graph) can be created in different ways, as in, we can use NFA approach but then we get a set of states after each char is fed, and when one of them is final set
we accept that char. But this approach is not ideal, so what we do is use KMP's intuition which suggestion that
we maintain transition states del(char, index), and as we already remember the set of char traveled to reach a particular state, simulation in next step
differs only in last symbol, so simply maintain an initial state x, the state after reading the longest prefix of the pattern we have found uptil then i.e., P[1....index); copy its transitions
update the initial state by following transitions for P[index]. */

/* Now, in search, we simply need to start from the first state of the automata and the first character of the text. At every step, we consider next character of text, 
look for the next state in the built automaton and move to a new state. If we reach the final state, then the pattern is found in the text.*/

// Pre-processing time: O(p*(const))
// Matching time: O(t)
// Where ‘p’ is length of pattern and ‘t’ is length of text.
// Space complexities: O((p+1)*(const)), to store shift during pre-processing.
// Where the const value is the number of characters.
// argc -> argument counter, argv -> c style strings (char pointers)
// arguments corresponding to command line: argv[0] -> file name, argv[1] = text, argv[2] = pattern

