// ->> Scroll to the bottom for the code and algorithm specifics.

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <unordered_map>

using namespace std;
class BoyerMoore
{
private:
    string pattern;
    unordered_map<char, int> amap;  
    vector<vector<int>> bad_char;
    vector<int> big_l, small_l_prime;

    vector<int> z_array(const string &s)
    {
        vector<int> z(s.length(), 0);
        int l = 0, r = 0;
        for (int i = 1; i < s.length(); ++i) {
            if (i <= r)
                z[i] = min(r - i + 1, z[i - l]);
            while (i + z[i] < s.length() && s[z[i]] == s[i + z[i]])
                ++z[i];
            if (i + z[i] - 1 > r)
                l = i, r = i + z[i] - 1;
        }
        return z;
    }

    vector<int> n_array(const string &s) {
        string rev_s = string(s.rbegin(), s.rend());
        vector<int> z_rev = z_array(rev_s);
        return vector<int>(z_rev.rbegin(), z_rev.rend());
    }

    vector<int> big_l_prime_array(const vector<int> &n) {
        vector<int> lp(pattern.length(), 0);
        for (int j = 0; j < pattern.length() - 1; ++j) {
            int i = pattern.length() - n[j];
            if (i < pattern.length())
                lp[i] = j + 1;
        }
        return lp;
    }

    vector<int> big_l_array(const vector<int> &lp) {
        vector<int> l(pattern.length(), 0);
        l[1] = lp[1];
        for (int i = 2; i < pattern.length(); ++i)
            l[i] = max(l[i - 1], lp[i]);
        return l;
    }

    vector<int> small_l_prime_array(const vector<int> &n) {
        vector<int> small_lp(n.size(), 0);
        for (int i = 0; i < n.size(); ++i)
            if (n[i] == i + 1)
                small_lp[pattern.length() - i - 1] = i + 1;

        for (int i = n.size() - 2; i >= 0; --i)
            if (small_lp[i] == 0)
                small_lp[i] = small_lp[i + 1];

        return small_lp;
    }

    vector<vector<int>> dense_bad_char_tab() {
        vector<vector<int>> tab(pattern.length(), vector<int>(amap.size(), 0));
        vector<int> nxt(amap.size(), 0);
        for (int i = 0; i < pattern.length(); ++i) {
            char c = pattern[i];
            tab[i] = nxt;
            nxt[amap[c]] = i + 1;
        }
        return tab;
    }

    void good_suffix_table() {
        vector<int> n = n_array(pattern);
        vector<int> lp = big_l_prime_array(n);
        big_l = big_l_array(lp);
        small_l_prime = small_l_prime_array(n);
    }

public:
    BoyerMoore(const string &p) : pattern(p) {

        string alphabet = "abcdefghijklmnopqrstuvwxyz";
        for (int i = 0; i < alphabet.size(); ++i)
            amap[alphabet[i]] = i;

        bad_char = dense_bad_char_tab();
        good_suffix_table();
    }

    int bad_character_rule(int i, char c) {
        if (amap.find(c) == amap.end())
            return i + 1; 
        return i - (bad_char[i][amap[c]] - 1);
    }

    int good_suffix_rule(int i) {
        int length = pattern.length();
        if (i == length - 1)
            return 0;
        ++i; 
        if (big_l[i] > 0)
            return length - big_l[i];
        return length - small_l_prime[i];
    }

    int match_skip() {
        return pattern.length() - small_l_prime[1];
    }
};

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

    vector<int> boyer_moore_search(const string &pattern)
    {
        BoyerMoore bm(pattern);
        vector<int> occurrences;
        size_t i = 0; // Keeping track of char's in pattern.
        size_t len_t = text.length();
        size_t len_p = pattern.length();

        while (i <= len_t - len_p) // Looping through all positions in text, where pattern could start.
        {
            int shift = 1;
            bool mismatched = false; // Update as we find a mismatch.
            for (int j = len_p - 1; j >= 0; --j)
            {
                if (pattern[j] != text[i + j])
                {
                    int bc_shift = bm.bad_character_rule(j, text[i + j]);
                    int gs_shift = bm.good_suffix_rule(j);
                    shift = max(shift, max(bc_shift, gs_shift));
                    // 3 possible shifts -> either by 1, by bc, or by gs. Settle with whatever is maximum.
                    mismatched = true;
                    break;
                }
            }
            if (!mismatched)
            {
                // Didn't found any mismatch, all char matched exactly.
                occurrences.push_back(i);
                shift = max(shift, bm.match_skip());
            }
            i += shift;
        }
        return occurrences;
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

    vector<int> occurrences = finder.boyer_moore_search(pattern);
    finder.display_output(pattern, occurrences);

    return 0;
}

/* z-array -> an array where each element z[i] represents the length of the longest substring 
starting from i that is also a prefix of the string passed. */  
/* n-array -> derived by sending the reverse of string in z-array, helps in good-suffix-rule
to calculate big-l-prime and small-l-prime.*/ 
// big-l-prime array -> finding largest suffix of substring to prefix of pattern match.
// big-l array -> max shift based on the match in suffix and prefix.
// small-l-prime array -> finding the shift when there is a partial match of prefix to suffix.
// dense-bad-char-table -> created from pattern and set of char's, using bc rule.
// good-suffix-table -> created using n-array, big-l-prime, small-l-prime, big-l.

/* bad-char-rule -> we pass the index of the pattern at which mismatch occurs, and the 
character in text which mismatched, it returns the no. of skips from the mapping/table 
corresponding to this rule. */ 
/* good-suffix-rule -> we only need to pass the index of the pattern where mismatch occurs. 
It returns no. of skips until a suffix of substring t of text, matches the prefix of pattern. */ 
/* match-skip -> pattern matches the text exactly, and it essentially just uses
good-suffix-rule in that case. */ 



// Pre-processing Time: ϴ(p+k), optimal for the cases where pattern is very large.
// Matching Time: a) Best Case: Ω(t/p) b) Worst Case: O(p*t)
// Where ‘p’ is length of pattern and ‘t’ is length of text.
// Space complexities: ϴ(m), to store shift during pre-processing.
// argc -> argument counter, argv -> c style strings (char pointers)
// arguments corresponding to command line: argv[0] -> file name, argv[1] = text, argv[2] = pattern