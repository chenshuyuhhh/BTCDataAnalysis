//
// Created by polarwk on 2021/8/21.
//
#include <sys/stat.h>
#include <iostream>
#include <string.h>
#include <fstream>
#include <stdio.h>
#include <vector>
#include <typeinfo>
#include <cstdio>
#include <sstream>
#include <map>
#include <stdio.h>
#include <unistd.h>
#include <dirent.h>
#include <stdlib.h>
#include <pthread.h>
#include <thread>
#include <ctime>
#include "nlohmann/json.hpp"
using json = nlohmann::json;

#ifndef TRANSACTIONLINKER_TRANSACTIONLINKER_H
#define TRANSACTIONLINKER_TRANSACTIONLINKER_H
using namespace std;


class TransactionLinker {
private:
    vector<string> date_files; // 所有的每天的交易文件路径
    int date_file_length; // 所有交易文件的数量
    string transaction_path; // 比特币交易存放的路径
    vector<vector<string>> lines;  // 要写入的交易信息
    map<string, string> utxos; // 未花费的交易输出
    string txs_wfile;        // 交易写入的路径 ******/result1.csv
    vector<string> spend_utxos; // 已花费交易输出的信息，要写到文件里。
    int num_threads;

public:
    TransactionLinker(string transaction_path);
    vector<string> split(string str, string pattern);
    void delete_utxo_and_result1();
//    void getAllFilesWithoutChildren(string path, vector<string>& files);
    bool isFileExists_stat(string& name);
    void all_file_link();
    void showAllFiles( const char * dir_name, vector<string>& files);
    void link_one_day(int begin, int end);
};


#endif //TRANSACTIONLINKER_TRANSACTIONLINKER_H
