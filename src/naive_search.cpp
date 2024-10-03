#include <iostream>
#include <vector>
#include <string>
#include <fstream>

using namespace std;

class OccurrenceFinder
{
private:
    string text;

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

    vector<int> naiveSearch(const string &pattern)
    {
        vector<int> occurrence;
        size_t len_t = text.length();
        size_t len_p = pattern.length();

        for (size_t i = 0; i <= len_t - len_p; i++)
        {
            bool match = true;
            for (size_t j = 0; j < len_p; j++)
            {
                if (text[i + j] != pattern[j])
                {
                    match = false;
                    break;
                }
            }
            if (match)
            {
                occurrence.push_back(i);
            }
        }
        return occurrence;
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
};

int main(int argc, char *argv[])
{
    if (argc < 3)
        return 1;
    OccurrenceFinder finder(argv[1]);
    string pattern(argv[2]);
    vector<int> occurrences = finder.naiveSearch(pattern);
    finder.display_output(pattern, occurrences);
    return 0;
}

// Best case: O(t)  Worst case: O(p*(t-p+1))
// Where ‘p’ is length of pattern and ‘t’ is length of text.
// Space complexities: O(1), since no extra space is required.
// argc -> argument counter, argv -> c style strings (char pointers)
// arguments corresponding to command line: argv[0] -> file name, argv[1] = text, argv[2] = pattern
