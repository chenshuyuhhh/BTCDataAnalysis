#include <iostream>
#include <string>
//#include <wsman.h>
#include <vector>
#include <fstream>
//#include <io.h>
#include "TransactionLinker.h"

using namespace std;


//void getFilesWithChildren(string path, vector<string>& files )
//{
//    //文件句柄
//    long  hFile = 0;
//    //文件信息
//    struct _finddata_t fileinfo;
//    string p;
//    if((hFile = _findfirst(p.assign(path).append("\\*").c_str(),&fileinfo)) !=  -1)
//    {
//        do
//        {
//            //如果是目录,迭代之
//            //如果不是,加入列表
//            if((fileinfo.attrib &  _A_SUBDIR))
//            {
//                if(strcmp(fileinfo.name,".") != 0  &&  strcmp(fileinfo.name,"..") != 0)
//                    getFilesWithChildren( p.assign(path).append("\\").append(fileinfo.name), files );
//            }
//            else
//            {
//                files.push_back(p.assign(path).append("\\").append(fileinfo.name) );
//            }
//        }while(_findnext(hFile, &fileinfo)  == 0);
//        _findclose(hFile);
//    }
//}
//
//void getAllFilesWithoutChildren(string path, vector<string>& files)
//{
//    // 文件句柄
//    long hFile = 0;
//    // 文件信息
//    struct _finddata_t fileinfo;
//
//    string p;
//
//    if ((hFile = _findfirst(p.assign(path).append("\\*").c_str(), &fileinfo)) != -1) {
//        do {
//            // 保存文件的全路径
//            files.push_back(p.assign(path).append("\\").append(fileinfo.name));
//
//        } while (_findnext(hFile, &fileinfo) == 0); //寻找下一个，成功返回0，否则-1
//
//        _findclose(hFile);
//    }
//}


int main() {
    TransactionLinker transactionLinker("/home/daslab/test_bitcoin_data");
    transactionLinker.delete_utxo_and_result1();
    transactionLinker.all_file_link();
}

