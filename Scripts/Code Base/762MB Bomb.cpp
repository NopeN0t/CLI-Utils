#ifdef _WIN32
    #include <windows.h>
#elif __linux__
    #include <pthread.h>
#endif

#include <iostream>
#include <fstream>
#include <thread>
#include <string>

using namespace std;
const auto PROCESSER_COUNT = 4;//thread::hardware_concurrency();

ofstream file[PROCESSER_COUNT];
int i;

#ifdef _WIN32
    DWORD WINAPI CreateJunk(LPVOID index){
        int fi = (int)*((int *)index) - 1;
        string fname = to_string(fi) + ".txt";
        file[fi].open(fname, ios::out | ios::app);
        for (int i = 0; i < 10000000; i++) file[fi] << ULONG_LONG_MAX; //Bigger The loop bigger the file (currently creating A burst of 762MB)
        file[fi].close();
        return 0;
    }
#endif

int main(){
    if (PROCESSER_COUNT == 0) exit(-1);
    #ifdef _WIN32
    cout << "Creating Threads " << PROCESSER_COUNT << endl;
        DWORD tid[PROCESSER_COUNT];
        HANDLE th[PROCESSER_COUNT];
        for(int i=0;i<PROCESSER_COUNT;i++){
            cout << "Thread " << i << "Created\n";
            th[i] = CreateThread(NULL,0,CreateJunk,(void *)&i,0,&tid[i]);
        }
          // Wait until all threads finish
        cout << "Threads Created" << endl;
	    for(int i=0;i<PROCESSER_COUNT;i++){
	    	if(th[i]!=NULL){
	    		WaitForSingleObject(th[i],INFINITE);
            }
        }
        // file.close();
        cout << "done\n";
        cin >> i;
        return 0;
    #endif
}