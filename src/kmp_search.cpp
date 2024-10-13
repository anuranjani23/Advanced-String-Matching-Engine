#include <iostream>
#include <vector>
#include <string>
#include <fstream>

using namespace std;

class OccurrenceFinder
{
private:
    string text;

    void computeLPSArray(const string &pattern, vector<int> &lps)
    {
        int M = pattern.length();
        int len = 0;  
        lps[0] = 0;   

        int i = 1;
        while (i < M)
        {
            if (pattern[i] == pattern[len])
            {
                len++;
                lps[i] = len;
                i++;
            }
            else
            {
                if (len != 0)
                {
                    len = lps[len - 1];  // do not increment i here.
                }
                else
                {
                    lps[i] = 0;
                    i++;
                }
            }
        }
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

    vector<int> KMPSearch(const string &pattern)
    {
        vector<int> occurrence;
        int M = pattern.length();
        int N = text.length();
        
        if (M == 0 || N == 0)
            return occurrence; 

        vector<int> lps(M, 0);  
        computeLPSArray(pattern, lps);

        int i = 0;  
        int j = 0;  

        while (i < N)
        {
            if (pattern[j] == text[i])
            {
                j++;
                i++;
            }

            if (j == M)
            {
                occurrence.push_back(i - j);
                j = lps[j - 1];
            }
            else if (i < N && pattern[j] != text[i])
            {
                if (j != 0)
                {
                    j = lps[j - 1];
                }
                else
                {
                    i++;
                }
            }
        }

        return occurrence;
    }

    void display_output(const string &pattern, const vector<int> &occurrences)
    {
        cout << pattern << ": ";
        if (occurrences.empty())
        {
            cout << "No occurrence found." << endl;
        }
        else
        {
            for (int index : occurrences)
            {
                cout << index << " ";
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
    string pattern(argv[2]);
    vector<int> occurrences = finder.KMPSearch(pattern);
    finder.display_output(pattern, occurrences);

    return 0;
}


/* LPS Array -> the pattern is pre-processed, where the the longest prefix that is also a suffix is calculated for each char,
that is, when matching the pattern with the text, if we find a mismatch, LPS array helps in finding the mismatched
charcter in our pattern, if it exists, and if it doesn't then to shift the entire pattern past the mismatched character.*/
// Pre-processing time: ϴ(p)
// Best case: Ω(t/p) b) Worst case: O(t*p)
// Where ‘p’ is length of pattern and ‘t’ is length of text.
// Space complexities: ϴ(p), to store shift during pre-processing.
// argc -> argument counter, argv -> c style strings (char pointers)
// arguments corresponding to command line: argv[0] -> file name, argv[1] = text, argv[2] = pattern
