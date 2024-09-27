#include <iostream>
#include <fstream>
#include <vector>
#include <string>

#define num_of_char 256
#define prime 113

using namespace std;
class OccurrenceFinder {
private:
    string text;
public:
    OccurrenceFinder(const string& filename) {
        ifstream fileIn(filename);
        if (!fileIn.is_open()) {
            cerr << "Error in opening: " << filename << endl;
            exit(EXIT_FAILURE);
        }
        text.assign((istreambuf_iterator<char>(fileIn)), istreambuf_iterator<char>());
        fileIn.close();
    }

    vector<int> RabinKarpSearch(const string& pattern){
        size_t len_t = text.length();
        size_t len_p = pattern.length();
        int p_hash = 0, t_hash = 0;
        int h = 1;
        vector<int> occurrence;
        
        for(int i = 0; i < len_p - 1; i++){
            h = (h*num_of_char)%prime; //h = d^(len_p - 1)
        }
        for(int i = 0; i < len_p; i++){
            p_hash = (num_of_char*p_hash + pattern[i])%prime;
            t_hash = (num_of_char*t_hash + text[i])%prime;
            //hash value calculation for pattern and text
        }
        for(int i = 0; i <= len_t - len_p; i++){
            if(p_hash == t_hash){
                bool match = true;
                for(int j = 0; j < len_p; j++){
                    if(text[i+j] != pattern[j]){
                        match = false;
                        break;
                    }
                }
                if(match){
                    occurrence.push_back(i);
                }
            }
            if(i < len_t - len_p){
                //slide over next window if hash values don't match
                t_hash = (num_of_char*(t_hash - text[i]*h) + text[i + len_p])%prime;
                
                //if hash value of text becomes negative
                if(t_hash < 0) t_hash += prime;
            }
        }
        return occurrence;
    }
    void display_output(const string& pattern, const vector<int>& occurrences) {
        cout << pattern << ":";
        if (occurrences.empty()) {
            cout << endl;
        } else {
            for (int index : occurrences) {
                cout << " " << index;
            }
            cout << endl;
        }
    }
};

int main(int argc, char* argv[]) {
    if(argc < 3) return 1;
    OccurrenceFinder finder(argv[1]);
    string pattern(argv[2]);
    vector<int> occurrences = finder.RabinKarpSearch(pattern);
    finder.display_output(pattern, occurrences);
    return 0;
}

// Pre-processing time: O(p), Compute Hashing in: O(1)
// Best and Average case: O(p+t), Worst case: O(p*(t-p+1))
// Where ‘p’ is length of pattern and ‘t’ is length of text.
// Space complexities: O(1) ->
// since pre-processing involves hashing of pattern which does not require extra space.
// argc -> argument counter, argv -> c style strings (char pointers)
// arguments corresponding to command line: argv[0] -> file name, argv[1] = text, argv[2] = pattern