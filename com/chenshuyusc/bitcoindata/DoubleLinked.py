import json
import redis
import pymysql
import _thread
import csv
import os

csv.field_size_limit(500 * 1024 * 1024)

host = 'localhost'
port = 3306
db = 'BTCData'
user = 'root'
password = '**'


# 根据原始交易文件获得信息
class DoubleLinked0:
    def __init__(self, basedir):
        # redis 连接池
        pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
        self._r = redis.Redis(connection_pool=pool)

        # 打开数据库连接
        # sqldb = pymysql.connect(host=host, user=user, password=password, db=db)
        # # mysql 数据库
        # # 使用cursor()方法获取操作游标
        # self._cursor = sqldb.cursor()

        self._t_lines = []
        self._t_line = []
        self._basedir = basedir
        self._years = []
        self._yearstimes = {}

        self.revlines = set()

    # 设计两个版本的redis
    # version1
    # txid     addr1#v1,addr2#v2,addr3#v3
    # 省内存，但是速度更慢，多一个取第几个
    #
    # version2
    # txid#index   addrv
    # 占内存，速度可能更快，但是key值增加，hash可能会变慢
    #
    # 所以v1和v2谁更好，说不准
    # 但是第一个对第二次链接更快

    def _write2SQL(self):
        print(self._t_line)
        # SQL 插入语句
        sql = "INSERT INTO  btc_tx (txhash,timestamp,size,version,n_in,n_out,locktime,vin,vout) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        print(sql)
        try:
            self._cursor.execute(sql, (
                self._t_line[7], self._t_line[6], self._t_line[1], self._t_line[0],
                self._t_line[3], self._t_line[4], self._t_line[2], self._t_line[5],
                self._t_line[6]))
            # self.t_line['txhash'], self.t_json['timestamp'], self.t_json['size'], self.t_json['version'],
            # self.t_json['n_in'], self.t_json['n_out'], self.t_json['locktime'], self.t_json['vin'],
            # self.t_json['vout'])
        except:
            print(self._t_line[7], " insert table failed")
            # print(self.t_json['txhash'], " insert table failed")

    # 针对v1的redis
    def _findIn(self):
        # 便于给交易输出链接提供信息
        timestamp = self._t_line[7]  # 时间戳 "timestamp"
        txhash = self._t_line[8]  # 交易 "txhash"

        # 存交易的输出信息和链接交易的输入，可以双线程？？？

        # 将交易的输出信息存储redis
        vouts = json.loads(self._t_line[6])  # 交易的输出 'vout'
        vout_info = vouts[0]['address'] + '#' + str(vouts[0]['value'])
        for i in range(1, len(vouts)):
            vout_info = vout_info + ',' + vouts[i]['address'] + '#' + str(vouts[i]['value'])
        self._r.set(txhash, vout_info)

        # 根据redis存储的信息，链接此交易的输入
        vins = json.loads(self._t_line[5])  # 交易输入，字符串转 json 对象 'vin'

        # 针对交易的每一笔输入，都更新
        for i in range(0, len(vins)):
            in_txid = vins[i]['txid']  # 输入的交易hash
            if '0000000000000000000000000000000000000000000000000000000000000000' == in_txid:
                # 创世交易，没有父交易，直接退出
                break

            in_num = int(vins[i]['vout'])  # 该交易输出的第几笔
            # 这里或许可以用多线程，一个线程负责链接此交易的输入，一个线程负责链接上一个交易的输出
            # 在redis数据库中根据txid和num找输入的具体值value
            # addr1#v1,addr2#v2,addr3#v3
            # 切割笔数
            all_in_list = self._r.get(in_txid).split(',')
            addrv = all_in_list[in_num].split('#')  # 输入的地址和金额

            # 将该交易的输入信息中的地址和金额补充完整
            vins[i]["address"] = addrv[0]
            vins[i]["value"] = float(addrv[1])

            # 更新redis数据库
            # # addr1#v1,addr2#v2,addr3#v3
            # &spent_timestamp#spent_tx
            # &标志已经被花费了
            all_in_list[in_num] = '&' + timestamp + '#' + txhash
            new_in = all_in_list[0]
            for i in range(1, len(all_in_list)):
                new_in += ","
                new_in += all_in_list[i]
            self._r.set(in_txid, new_in)

        # 循环结束，交易的输入链接完毕

        # 更新交易
        self._t_line[5] = json.dumps(vins)  # vin
        # 将新的交易信息写入数据库
        # self._write2SQL()

    # 多个交易时间一样时的链接
    def _findMultiIn(self):
        # 将时间一样的所有交易存入redis
        for line in self._t_lines:
            # 将交易的输出信息存储redis
            vouts = json.loads(line[6])  # 交易的输出 'vout'
            vout_info = vouts[0]['address'] + '#' + str(vouts[0]['value'])
            for i in range(1, len(vouts)):
                vout_info = vout_info + ',' + vouts[i]['address'] + '#' + str(vouts[i]['value'])
            self._r.set(line[8], vout_info)  # line[8] 交易哈希

        for i in range(0, len(self._t_lines)):
            line = self._t_lines[i]
            # 根据redis存储的信息，链接此交易的输入
            vins = json.loads(line[5])  # 交易输入，字符串转 json 对象 'vin'
            # 便于给交易输出链接提供信息
            timestamp = line[7]  # 时间戳 "timestamp"
            txhash = line[8]  # 交易 "txhash"

            # 针对交易的每一笔输入，都更新
            for j in range(0, len(vins)):
                in_txid = vins[j]['txid']  # 输入的交易hash
                if '0000000000000000000000000000000000000000000000000000000000000000' == in_txid:
                    # 创世交易，没有父交易，直接退出
                    break

                in_num = int(vins[j]['vout'])  # 该交易输出的第几笔
                # 这里或许可以用多线程，一个线程负责链接此交易的输入，一个线程负责链接上一个交易的输出
                # 在redis数据库中根据txid和num找输入的具体值value
                # addr1#v1,addr2#v2,addr3#v3
                # 切割笔数
                all_in_list = self._r.get(in_txid).split(',')
                addrv = all_in_list[in_num].split('#')  # 输入的地址和金额

                # 将该交易的输入信息中的地址和金额补充完整
                vins[j]["address"] = addrv[0]
                vins[j]["value"] = float(addrv[1])

                # 更新redis数据库
                # # addr1#v1,addr2#v2,addr3#v3
                # &spent_timestamp#spent_tx
                # &标志已经被花费了
                all_in_list[in_num] = '&' + timestamp + '#' + txhash
                new_in = all_in_list[0]
                for j in range(1, len(all_in_list)):
                    new_in += ","
                    new_in += all_in_list[j]
                self._r.set(in_txid, new_in)

            # 更新交易
            self._t_lines[i][5] = json.dumps(vins)  # vin

    def _findOut(self):
        txid = self._t_line[8]  # 交易 "txhash"
        outs = json.loads(self._t_line[6])  # 交易的输出 'vout'

        # addr1#v1,addr2#v2,addr3#v3
        # &spent_timestamp#spent_tx
        # &标志已经被花费了
        if self._r.exists(txid):
            content = self._r.get(txid).split(',')
            # 从redis删除此条交易记录
            self._r.delete(txid)
            if len(content) != len(outs):
                # 这里应该抛异常
                print('error')

            # 补充输出是否被花费
            for i in range(0, len(content)):
                if content[i][0] is '&':
                    out = content[i][1:].split('#')
                    outs[i]["spent_timestamp"] = int(out[0])
                    outs[i]["spent_tx"] = out[1]

            # 更新输出信息
            self._t_line[6] = json.dumps(outs)

    # 根据文件filename，遍历每一行
    # 每一行是一笔交易
    # 找这个交易的输入具体信息
    def _onefileIn(self, filename, rbasedir, wbasedir):
        fr = list(csv.reader(open(rbasedir + '/' + filename, 'r'), delimiter=';'))
        print(rbasedir + '/' + filename)
        fw = csv.writer(open(wbasedir + '/' + filename, 'w'), delimiter=';')

        # 只有一条交易信息，不存在时间戳一样
        if len(fr) == 1:
            self._t_line = fr[0]
            # 找这个交易的输入信息，并更新交易信息
            self._findIn()
            # 写入新的交易信息
            fw.writerow(self._t_line)
        else:  # 不止一条交易信息，可能时间戳一样。
            # 第0条假的交易数据，是为了接住前面的交易信息
            temp_line = fr[0]
            lines = []  # 存有相同交易时间的交易信息，将具有相同时间戳的交易看作一个整体，一起处理
            lines.append(temp_line)

            # 文件中的每一行
            for i in range(1, len(fr)):
                if fr[i][7] != temp_line[7]:  # 时间戳和上一个不一样，就可以把之前的都更新了
                    self._t_lines = lines
                    # 找这些时间戳一样的交易输入
                    self._findMultiIn()
                    # 写入文件
                    fw.writerows(self._t_lines)
                    lines.clear()  # 清空
                temp_line = fr[i]
                lines.append(temp_line)

            # 最后肯定有没有链接的交易
            self._t_lines = lines
            self._findMultiIn()
            fw.writerows(self._t_lines)

    def _oneTIn(self, line):
        # 根据redis存储的信息，链接此交易的输入
        vins = json.loads(line[5])  # 交易输入，字符串转 json 对象 'vin'
        # 便于给交易输出链接提供信息
        timestamp = line[7]  # 时间戳 "timestamp"
        txhash = line[8]  # 交易 "txhash"

        # 针对交易的每一笔输入，都更新
        for j in range(0, len(vins)):
            in_txid = vins[j]['txid']  # 输入的交易hash
            if '0000000000000000000000000000000000000000000000000000000000000000' == in_txid:
                # 创世交易，没有父交易，直接退出
                break

            in_num = int(vins[j]['vout'])  # 该交易输出的第几笔
            # 这里或许可以用多线程，一个线程负责链接此交易的输入，一个线程负责链接上一个交易的输出
            # 在redis数据库中根据txid和num找输入的具体值value
            # addr1#v1,addr2#v2,addr3#v3
            # 切割笔数
            if not self._r.exists(in_txid):
                print('not exist')
                print(in_txid)
                print(txhash)
                self.revlines.add(in_txid)
                # 没找到，存着后续找
                continue
            all_in_list = self._r.get(in_txid).split(',')

            addrv = all_in_list[in_num].split('#')  # 输入的地址和金额

            # 将该交易的输入信息中的地址和金额补充完整
            vins[j]["address"] = addrv[0]
            vins[j]["value"] = float(addrv[1])

            # 更新redis数据库
            # # addr1#v1,addr2#v2,addr3#v3
            # &spent_timestamp#spent_tx
            # &标志已经被花费了
            all_in_list[in_num] = '&' + timestamp + '#' + txhash
            new_in = all_in_list[0]
            for k in range(1, len(all_in_list)):
                new_in = new_in + "," + all_in_list[k]
            self._r.set(in_txid, new_in)

        return vins

    def _onefileAllIn(self, filename, rbasedir, wbasedir):
        fr = list(csv.reader(open(rbasedir + '/' + filename, 'r'), delimiter=';'))
        fw = csv.writer(open(wbasedir + '/' + filename, 'w'), delimiter=';')

        # 只有一条交易信息，不存在时间戳一样
        if len(fr) == 1:
            self._t_line = fr[0]
            # 找这个交易的输入信息，并更新交易信息
            self._findIn()
            # 写入新的交易信息
            fw.writerow(self._t_line)
        else:  # 不止一条交易信息
            # 文件中的每一行
            # 将这一天所有的交易的输出信息存储redis
            for line in fr:
                vouts = json.loads(line[6])  # 交易的输出 'vout'
                vout_info = vouts[0]['address'] + '#' + str(vouts[0]['value'])
                for i in range(1, len(vouts)):
                    vout_info = vout_info + ',' + vouts[i]['address'] + '#' + str(vouts[i]['value'])
                self._r.set(line[8], vout_info)  # line[8] 交易哈希

            # for line in self.revlines:
            #     self._oneTIn(line)

            for i in range(0, len(fr)):
                # 做输入的链接，并更新交易的输入
                fr[i][5] = json.dumps(self._oneTIn(fr[i]))  # vin
            fw.writerows(fr)

    # 根据文件filename，遍历每一行
    # 每一行是一笔交易
    # 找这个交易的输出具体信息
    def _onefileOut(self, filename, rbasedir, wbasedir):
        fr = csv.reader(open(rbasedir + '/' + filename, 'r', encoding='UTF-8'), delimiter=';')
        fw = csv.writer(open(wbasedir + '/' + filename, 'w'), delimiter=';')
        for line in fr:
            self._t_line = line
            self._findOut()
            fw.writerow(self._t_line)

    # 获取列表的第二个元素
    def _takeTimestamp(self, elem: list):
        return elem[7]

    def _sortTs(self, filename):
        fr = open(filename, 'r+')
        fr_list = list(csv.reader(fr, delimiter=';'))
        fr.close()

        if len(fr_list) < 2:
            return
        fr_list.sort(key=self._takeTimestamp)
        fw = open(filename, 'w')
        fwcsv = csv.writer(fw, delimiter=';')
        fwcsv.writerows(fr_list)
        fw.close()

    def sortAllFiles(self):
        basedir = self._basedir + "/data/"

        self._years = os.listdir(basedir)
        self._years.sort()

        for year in self._years:
            print(year)
            times = os.listdir(basedir + year)
            times.sort()
            self._yearstimes[year] = times
            for time in times:
                # 年份下面没有文件，删掉这个目录
                if not os.path.exists(basedir + year + '/' + time + '/result.csv'):
                    os.removedirs(basedir + year + '/' + time)
                else:
                    self._sortTs(basedir + year + '/' + time + '/result.csv')

    # 如果预先排好顺序，就需要使用这个接口，获得目录年份和时间
    # 如果没有排好顺序，直接调用sortAllFiles，既可以排序，又可以获得目录年份和时间
    def getYearsAndTimes(self):
        basedir = self._basedir + "/data/"

        self._years = os.listdir(basedir)
        self._years.sort()

        for year in self._years:
            times = os.listdir(basedir + year)
            times.sort()
            self._yearstimes[year] = times

    def doublelinked(self):
        # 可以直接覆盖写
        rbasedir = self._basedir + "/data"
        wbasedir1 = self._basedir + "/data2"
        wbasedir2 = self._basedir + "/data3"

        for year in self._years:
            print(year)
            if not os.path.exists(wbasedir1 + '/' + year):
                os.makedirs(wbasedir1 + '/' + year)
            for time in self._yearstimes[year]:
                if not os.path.exists(wbasedir1 + '/' + year + '/' + time):
                    os.makedirs(wbasedir1 + '/' + year + "/" + time)

                # 输入链接
                self._onefileAllIn('result.csv', rbasedir + "/" + year + '/' + time,
                                   wbasedir1 + '/' + year + '/' + time)

        for year in self._years:
            if not os.path.exists(wbasedir2 + '/' + year):
                os.makedirs(wbasedir2 + '/' + year)
            for time in self._yearstimes[year]:
                if not os.path.exists(wbasedir2 + '/' + year + '/' + time):
                    os.makedirs(wbasedir2 + '/' + year + '/' + time)

                print(time)
                self._onefileOut('result.csv', rbasedir + '/' + year + '/' + time, wbasedir2 + '/' + year + '/' + time)
