void search(char pat[],char txt[],int prime){
    int M= strlen(pat);
    int N= strlen(txt);
    int i,j;
    int h=1;
    int p=0;//hash value of pattern
    int t=0;//hash value of text 
    int d=256;
    int prime=INT_MAX;
    //
    for(i=0;i<M-1;i++)
    h=(h*d)%prime;

    for(i=0;i<M;i++){
        p=(p*d+pat[i])%prime;
        t=(t*d+txt[i])%prime;
    }

    for(i=0;i<N-M;i++){
     if(p==t){
        for( j=0;j<M;j++){
              if(txt[i+j]!=pat[j]){
                break;
              }
        }
        if(j==M){
            cout<<"pattern match at"<<i<<endl;
        }
     }
     if(i<N-M){
        t=(((t-txt[i]*h)*d)+txt[i+M])%prime;
  }
 
    }
}
