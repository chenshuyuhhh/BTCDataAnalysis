//
// Created by polarwk on 2021/8/21.
//

#include "TransactionLinker.h"


void TransactionLinker::showAllFiles(const char * dir_name, vector<string>& files)
{

    // check if dir_name is a valid dir
    struct stat s;
    lstat( dir_name , &s );
//    if( ! S_ISDIR( s.st_mode ) )
//    {
//        cout<<"dir_name is not a valid directory !"<<endl;
//        return;
//    }

    struct dirent * filename;    // return value for readdir()
    DIR * dir;                   // return value for opendir()
    dir = opendir( dir_name );

    string p;
    /* read all the files in the dir ~ */
    while( ( filename = readdir(dir) ) != NULL )
    {
        // get rid of "." and ".."
        if( strcmp( filename->d_name , "." ) == 0 ||
        strcmp( filename->d_name , "..") == 0    )
            continue;
        files.push_back(p.assign(dir_name).append("/").append(filename->d_name));
    }
    sort(files.begin(), files.end());
    closedir(dir);
}

bool TransactionLinker::isFileExists_stat(string& name) {
    struct stat buffer;
    return (stat(name.c_str(), &buffer) == 0);
}

void TransactionLinker::delete_utxo_and_result1() {
    vector<string> years;
    showAllFiles(transaction_path.c_str(), years);
    for (int i = 0; i < years.size(); ++i) {
        vector<string> dates;
        showAllFiles(years[i].c_str(), dates);
        for (int j = 0; j < dates.size(); ++j) {
            string result1_path = dates[j] + "/result1.csv";
            const char *del_file = result1_path.data();
            if (isFileExists_stat(result1_path)){
                remove(del_file);
            }

            string utxo_path = dates[j] + "/utxo.csv";
            const char *del_utxo_file = utxo_path.data();
            if (isFileExists_stat(utxo_path)){
                remove(del_utxo_file);
            }
        }
    }
    cout<<"delete result1 and utxo finish"<<endl;
}

TransactionLinker::TransactionLinker(string transaction_path) {
    this->transaction_path = std::move(transaction_path);
    vector<string> years;
    showAllFiles(this->transaction_path.c_str(), years);
    for (int i = 0; i < years.size(); ++i) {
        vector<string> dates;
        showAllFiles(years[i].c_str(), dates);
        for (int j = 0; j < dates.size(); ++j) {
            date_files.push_back(dates[j].append("/"));
        }
    }
    date_file_length = date_files.size();
    cout<<"TransactionLinker init"<<endl;
}


void TransactionLinker::all_file_link() {
    time_t now = time(0);
    string dt = ctime(&now);
    cout << "start: " + dt << endl;
    // 先将第一个交易文件，加载到内存里
    vector<vector<string>> txs_lines; // 一天的所有交易
    ifstream fp(this->date_files[0] + "result.csv");
    this->txs_wfile = this->date_files[0] + "result1.csv";
    string line;     // 每一行交易
    while (getline(fp, line)){
        vector<string> data_line;
        string item;
        istringstream readstr(line); //string数据流化
        //将一行数据按'，'分割
        for(int j = 0; j < 9;j++){ //可根据数据的实际情况取循环获取
            getline(readstr,item,';'); //循环读取数据
            data_line.push_back(item);
        }
        txs_lines.push_back(data_line); //插入到vector中
    }  // 将一个csv文件加载到txs_lines
    this->lines = txs_lines;
    cout<<"first txs_file read finish"<<endl;


    // 将txs_lines中的utxo放到内存里map里
    for (int i = 0; i < txs_lines.size(); ++i) {
        string outputs_str = txs_lines[i][6];   // utxo加入到map中
        string txhash = txs_lines[i][8];
        txhash.pop_back();
        string time = txs_lines[i][7];
        auto outputs = json::parse(outputs_str);
        for (int j = 0; j < outputs.size(); ++j) {
            this->utxos[txhash + "#" + to_string(j)] = to_string(outputs[j]["address"]) + "#" + to_string(outputs[j]["value"]) + "#" + time;
        }
    }
    cout<<"first txs_file load map finish"<<endl;

    for (int i = 1; i < date_file_length; ++i) {
        time_t now = time(0);
        string dt = ctime(&now);
        cout <<this->date_files[i] +  " start: " + dt << endl;
        vector<vector<string>> txs_lines;
        ifstream fp(this->date_files[i] + "result.csv");
        string line;
        while (getline(fp, line)){
            vector<string> data_line;
            string item;
            istringstream readstr(line); //string数据流化
            //将一行数据按'，'分割
            for(int j = 0; j < 9;j++){ //可根据数据的实际情况取循环获取
                getline(readstr,item,';'); //循环读取数据
                data_line.push_back(item);
            }
            txs_lines.push_back(data_line); //插入到vector中
        }
//        cout<< to_string(i) + " txs_file read finish" << endl;

        // 将txs_lines中的utxo放到内存里map里
        for (int j = 0; j < txs_lines.size(); ++j) {
            string outputs_str = txs_lines[j][6];   // utxo加入到map中
            string txhash = txs_lines[j][8];
            txhash.pop_back();
            string time = txs_lines[j][7];
            auto outputs = json::parse(outputs_str);
            for (int k = 0; k < outputs.size(); ++k) {
                this->utxos[txhash + "#" + to_string(k)] = to_string(outputs[k]["address"]) + "#" + to_string(outputs[k]["value"]) + "#" + time;
            }
        }
//        cout<<to_string(i) + " txs_file load map finish"<<endl;

        // 从内存中补全交易输入中的address和value字段
        int txs_lines_length = this->lines.size();
        cout<<txs_lines_length<<endl;
//        this->link_one_day(0, txs_lines_length);

        if (txs_lines_length <= 10000){
            link_one_day(0, txs_lines_length);
        }else{
            vector<thread> tids;
            int k = 0;
            while (k < txs_lines_length){
                if (k + 10000 > txs_lines_length){
                    tids.push_back(thread(&TransactionLinker::link_one_day, this, k, txs_lines_length));
                    break;
                }else{
                    tids.push_back(thread(&TransactionLinker::link_one_day, this, k, k+10000));
                    k += 10000;

                }
            }
            for (vector<thread>::iterator it = tids.begin(); it != tids.end(); it++) {
                it->join();  //主线程等待子线程
            }
        }


//        cout<<to_string(i) + " find finish"<<endl;

        // 将补全交易输入字段的交易写入文件
        ofstream outFile;
        outFile.open(this->txs_wfile, ios::ate);
        for (int j = 0; j < this->lines.size(); ++j) {
            for (int k = 0; k < 8; ++k) {
                outFile << this->lines[j][k] << ';';
            }
            outFile<<this->lines[j][8] << endl;
        }
        cout<<this->date_files[i] + + " write finish" << endl;
        this->lines = txs_lines;
        this->txs_wfile = this->date_files[i] + "result1.csv";

    }
}


void TransactionLinker::link_one_day(int begin, int end){
    cout<< begin << "   " << end<<endl;
    for (int i = begin; i < end; ++i) {
        auto inputs = json::parse(this->lines[i][5]);
        string time = this->lines[i][7];
        for (int k = 0; k < inputs.size(); ++k) {
            string prev_id = inputs[k]["txid"];
            string vout = inputs[k]["vout"];
            if (prev_id.compare("0000000000000000000000000000000000000000000000000000000000000000") == 0){
                break;
            }

            string information;
            information = this->utxos[prev_id + "#" + vout];

            vector<string> utxo = this->split(information, "#");
            inputs[k]["address"] = utxo[0];
            inputs[k]["value"] = utxo[1];

            this->utxos.erase(prev_id + "#" + vout);
        }
        this->lines[i][5] = inputs.dump();
    }
}



vector<string> TransactionLinker::split(string str, string pattern){
    int pos;
    vector<string> result;
    str += pattern;
    int size = str.size();
    for (int i = 0; i < size; ++i) {
        pos = str.find(pattern, i);
        if(pos < size){
            string s = str.substr(i, pos - i);
            result.push_back(s);
            i = pos + pattern.size() - 1;
        }
    }
    return result;
}

