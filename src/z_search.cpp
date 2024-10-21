// ->> Scroll to the bottom for the code and algorithm specifics.

#include <iostream>
#include <fstream>
#include <vector>
#include <string>

#define num_of_char 256

using namespace std;
class OccurrenceFinder
{
private:
    string text;

    vector<int> z_function(const string &s) {
        int n = s.size();
        vector<int> z(n, 0);
        int l = 0, r = 0;
        for (int i = 1; i < n; i++) {
            if (i < r) {
                z[i] = min(r - i, z[i - l]);
            }
            while (i + z[i] < n && s[z[i]] == s[i + z[i]]) {
                z[i]++;
            }
            if (i + z[i] > r) {
                l = i;
                r = i + z[i];
            }
        }
        return z;
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

    vector<int> ZSearch(const string &pattern) {
        size_t len_t = text.length();
        size_t len_p = pattern.length();
        vector<int> occurrence;

        string combined = pattern + "$" + text;

        vector<int> z = z_function(combined);

        for (size_t i = len_p + 1; i < z.size(); i++) {
            if (z[i] == len_p) {
                occurrence.push_back(i - len_p - 1); 
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
    vector<int> occurrences = finder.ZSearch(pattern);
    finder.display_output(pattern, occurrences);
    return 0;
}

/* In ZSearch we construct the Z-array, to compute which we concatenate pattern, text, and an arbitrary symbol say "$" as: pattern+"$"+text.
We do this to compute the values for each index in Z-array, each value (Z[index]) here signifies the length of longest substring starting from 
index position which is also a prefix of the combined string. */

/* After this array is computed we just have to search for the occurrence of the length of pattern in this array, and return the occurrences. */


// Pre-processing time: O(p+t)
// Matching time: O(p+t) 
// Where ‘p’ is length of pattern and ‘t’ is length of text.
// Space complexities: O(p+t) —> Space for storing the Z-array.
// argc -> argument counter, argv -> c style strings (char pointers)
// arguments corresponding to command line: argv[0] -> file name, argv[1] = text, argv[2] = pattern