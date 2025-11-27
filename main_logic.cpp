#include<iostream>
#include<vector>
#include<string>
#include<list>
#include<unordered_map>
using namespace std;

void take_input(vector<int>& inputs){
    int n;
    cout<<"Enter the number of process: ";
    cin>>n;
    int val;
    cout<<"Enter the Process";
    for(int i=0;i<n;i++){
        cin>>val;
        inputs.push_back(val);
    }
}

int main(){
    vector<int> inputs;
    take_input(inputs);
    vector<int> ram(3,-1);
    list<int> check_usage;
    unordered_map<int, list<int>::iterator> map;
    int ram_size=0;

    for(int i=0;i<inputs.size();i++){
        cout<<"Access "<<inputs[i]<<": ";
        if(map.find(inputs[i]) != map.end()){
            cout<<"HIT -> [";
            check_usage.splice(check_usage.begin(), check_usage, map[inputs[i]]);
        }else{
            cout<<"MISS -> [";
            int victim=-1;
            if(check_usage.size()==3){
                victim=check_usage.back();
                check_usage.pop_back();
                map.erase(victim);
            }
            check_usage.push_front(inputs[i]);
            map[inputs[i]]=check_usage.begin();
            // bool placed=false;
            for(int j=0;j<3;j++){
                if(ram[j]==-1){
                    ram[j]=inputs[i];
                    // placed=true;
                    break;
                }
                if(ram[j]==victim){
                    ram[j]=inputs[i];
                    // placed=true;
                    break;
                }
            }
        }
        for(int j=0;j<3;j++){
            cout<<ram[j]<<" ";
        }
        cout<<"]"<<endl;
    }
}