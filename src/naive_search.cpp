#include <iostream>
#include <vector>
#include <string>
#include <fstream>

using namespace std;

vector<int> naiveSearch(const string& txt, const string& pat, const vector<int>& o){
    vector<int> occurrence;
    size_t len_t = txt.length();
    size_t len_p = pat.length();
    bool match = true;
    for(int i = 0; i < len_t - len_p + 1; i++){
        for(int j = 0; j < len_p; j++){
            if(txt[i + j] != pat[j])
                match = false;
                break;
            if(match)
                occurrence.push_back(i);
        }
    }
    return occurrence;
}

int main(){
    ifstream fileIn;
    fileIn.open("sample.txt");
    if(!fileIn.is_open()){
        cerr << "Error in opening: sample.txt" << endl;
        return -1;  
    }
    string text((istreambuf_iterator<char>(fileIn)), istreambuf_iterator<char>());
    fileIn.close();
    return 0;
}

//Best case: O(t)  Worst case: O(p*(t-p+1))
//Where ‘p’ is length of pattern and ‘t’ is length of text.
//Space complexities: O(1), since no extra space is required.