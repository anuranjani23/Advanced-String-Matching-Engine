#include <iostream>
#include <vector>
#include <unordered_map>
#include <string>
#include <algorithm>

using namespace std;

//find the longest substring starting from each index i that matches prefix
//
vector<int> z_array(const string& s){
    int n = s.size();
    vector<int> z(n,0);
    int l = 0, r = 0;

    for(int i = 1; i < n; i++){
        if(i<=r){
            z[i] = min(r-i+1, z[i-1]);
        }
        while(i + z[i] < n && s[z[i]] == s[i+z[i]]){
            z[i]++;
        }
        if(i+z[i]-1 > r){
            l = i;
            r = i+z[i]-1;
        }
    }
    return z;
}

vector<int> n_array(const string& s){
    string rev_s = s;
    reverse(rev_s.begin(), rev_s.end());
    return z_array(rev_s);
}

vector<int> 