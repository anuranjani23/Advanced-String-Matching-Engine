#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <queue>
#include <cctype>
#include <cstring>

using namespace std;

class OccurrenceFinder
{
private:
    string text;
    static const int MAXS = 500;
    static const int MAXC = 52;
    int out[MAXS];
    int f[MAXS];
    int g[MAXS][MAXC];

    int charToIndex(char ch)
    {
        if (islower(ch)) return ch - 'a';
        if (isupper(ch)) return ch - 'A' + 26;
        return -1;
    }

    void buildMatchingMachine(const vector<string> &patterns)
    {
        memset(out, 0, sizeof(out));
        memset(g, -1, sizeof(g));

        int states = 1;

        for (const string &pattern : patterns)
        {
            int currentState = 0;
            for (char ch : pattern)
            {
                int index = charToIndex(ch);
                if (index == -1) continue;
                if (g[currentState][index] == -1)
                {
                    g[currentState][index] = states++;
                }
                currentState = g[currentState][index];
            }
            out[currentState] = 1;
        }

        for (int ch = 0; ch < MAXC; ++ch)
        {
            if (g[0][ch] == -1)
            {
                g[0][ch] = 0;
            }
        }

        memset(f, -1, sizeof(f));
        queue<int> q;

        for (int ch = 0; ch < MAXC; ++ch)
        {
            if (g[0][ch] != 0)
            {
                f[g[0][ch]] = 0;
                q.push(g[0][ch]);
            }
        }

        while (!q.empty())
        {
            int state = q.front();
            q.pop();

            for (int ch = 0; ch < MAXC; ++ch)
            {
                if (g[state][ch] != -1)
                {
                    int failure = f[state];
                    while (g[failure][ch] == -1)
                    {
                        failure = f[failure];
                    }
                    failure = g[failure][ch];
                    f[g[state][ch]] = failure;
                    out[g[state][ch]] |= out[failure];
                    q.push(g[state][ch]);
                }
            }
        }
    }

    int findNextState(int currentState, char nextInput)
    {
        int ch = charToIndex(nextInput);
        if (ch == -1) return currentState;

        while (g[currentState][ch] == -1)
        {
            currentState = f[currentState];
        }
        return g[currentState][ch];
    }

public:
    OccurrenceFinder(const string &filename)
    {
        ifstream fileIn(filename);
        if (!fileIn.is_open())
        {
            cerr << "Error in opening: " << filename << endl;
            exit(EXIT_FAILURE);
        }

        text.assign((istreambuf_iterator<char>(fileIn)), istreambuf_iterator<char>());
        fileIn.close();
    }

    vector<int> search(const string &pattern)
    {
        buildMatchingMachine({pattern});
        vector<int> occurrences;

        int currentState = 0;
        int lastMatch = -1;

        for (int i = 0; i < text.size(); ++i)
        {
            currentState = findNextState(currentState, text[i]);

            if (out[currentState] == 1)
            {
                int matchIndex = i - pattern.size() + 1;
                if (matchIndex != lastMatch + 1)
                {
                    occurrences.push_back(matchIndex);
                    lastMatch = matchIndex;
                }
            }
        }

        return occurrences;
    }

    void display_output(const string &pattern, const vector<int> &occurrences)
    {
        cout << pattern << ":";
        if (!occurrences.empty())
        {
            for (int index : occurrences)
            {
                cout << " " << index;
            }
            cout << endl;
        }
    }
};

int main(int argc, char *argv[])
{
    if (argc < 3)
    {
        cerr << "Usage: " << argv[0] << " <filename> <pattern>" << endl;
        return 1;
    }
    OccurrenceFinder finder(argv[1]);
    string pattern = argv[2];

    vector<int> occurrences = finder.search(pattern);
    finder.display_output(pattern, occurrences);
    return 0;
}



/*
The Aho-Corasick algorithm creates a finite state automaton from a set of patterns. The automaton is built by inserting each pattern into a directed graph where each state corresponds to a prefix of a pattern. Each transition corresponds to a character in the alphabet.
After constructing the automaton, the text is processed character by character. At each character, the current state changes according to the automaton's transitions.
If the automaton reaches a final state (which corresponds to a complete match of a pattern), the starting index of the
matched pattern in the text is recorded as an occurrence.
The automaton utilizes a failure function to efficiently handle mismatches. If a character does not lead to a valid transition, the automaton falls back to the
longest prefix that is also a suffix, allowing for continued processing without starting over.

Pre-processing time: O(m * |Σ|), where m is the total length of all patterns and |Σ| is the size of the alphabet.
Matching time: O(n), where n is the length of the text.
Space complexity: O(m * |Σ|) to store the automaton and failure functions.
*/
