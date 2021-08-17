import json
import redis
import pymysql
import csv
import os

csv.field_size_limit(500 * 1024 * 1024)

host = 'localhost'
port = 3306
db = 'BTCData'
user = 'root'
password = '**'


# 根据原始交易文件获得信息
class DoubleLinked2:
    def __init__(self, basedir):
        # redis 连接池
        # txid#index   addrv
        pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
        self._r = redis.Redis(connection_pool=pool)

        # 打开数据库连接
        self._sqldb = pymysql.connect(host=host, user=user, password=password, db=db)
        # mysql 数据库
        # 使用cursor()方法获取操作游标
        self._cursor = self._sqldb.cursor()

        self._basedir = basedir

    def _findTOut(self, line):
        txid = line[8]  # 交易 "txhash"
        vouts = json.loads(line[6])  # 交易的输出 'vout'

        for i in range(0, len(vouts)):
            key = txid + '#' + str(i)

            # redis 里没有，就说明已经被花费了
            # 从mysql里找
            if not self._r.exists(key):
                findsql = "SELECT spend_time,spend_tx  FROM utxos where txhashnum = '%s'" % (key)

                try:
                    # 执行SQL语句
                    self._cursor.execute(findsql)
                    spend_time, spend_tx = self._cursor.fetchone()

                    vouts[i]["spend_time"] = spend_time
                    vouts[i]["spent_tx"] = spend_tx

                    # remove the key
                    deletesql = "DELETE FROM utxos WHERE  txhashnum = '%s'" % (key)

                    # 执行SQL语句
                    self._cursor.execute(deletesql)
                    self._sqldb.commit()
                except:
                    print('failed')

        return vouts

    def _findTIn(self, line):
        # 根据redis存储的信息，链接此交易的输入
        vins = json.loads(line[5])  # 交易输入，字符串转 json 对象 'vin'
        # 便于给交易输出链接提供信息
        # timestamp = line[7]  # 时间戳 "timestamp"
        txhash = line[8]  # 交易 "txhash"

        # 针对交易的每一笔输入，都更新
        for j in range(0, len(vins)):
            in_txid = vins[j]['txid']  # 输入的交易hash
            if '0000000000000000000000000000000000000000000000000000000000000000' == in_txid:
                # 创世交易，没有父交易，直接退出
                break

            # txid#index   addr#v
            key = in_txid + '#' + vins[j]['vout']

            if not self._r.exists(key):
                print('not exist')
                print(in_txid)
                print(txhash)
                # self.revlines.add(in_txid)
                # 没找到，存着后续找
                # 暂时侥幸心里，不管
                continue

            # 在redis数据库中根据txid和num找输入的具体值
            addrv = self._r.get(key).split('#')  # 输入的地址和金额

            # 将该交易的输入信息中的地址和金额补充完整
            vins[j]["address"] = addrv[0]
            vins[j]["value"] = float(addrv[1])

            # 写入持久化数据库
            utxosql = "INSERT INTO utxos (txhashnum,spend_time,spend_tx) VALUES ('%s',%s,'%s')" % (key, line[7], txhash)
            try:
                self._cursor.execute(utxosql)
                self._sqldb.commit()
                # print('success!!!', utxosql)
            except:
                # print(utxosql)
                print('insert failed')

            # 从redis中删除
            self._r.delete(key)

        return vins

    def _vout2redis(self, txhash, vouts):
        for i in range(0, len(vouts)):
            self._r.set(txhash + '#' + str(i), vouts[i]['address'] + '#' + str(vouts[i]['value']))  # line[8] 交易哈希

    # 对整个文件链接输入
    def _onefileAllIn(self, filename, rbasedir, wbasedir):
        fr = list(csv.reader(open(rbasedir + '/' + filename, 'r'), delimiter=';'))
        fw = csv.writer(open(wbasedir + '/' + filename, 'w'), delimiter=';')

        for line in fr:
            self._vout2redis(txhash=line[8], vouts=json.loads(line[6]))

        for i in range(0, len(fr)):
            # 做输入的链接，并更新交易的输入
            fr[i][5] = json.dumps(self._findTIn(fr[i]))  # vin
        fw.writerows(fr)

    # 根据文件filename，遍历每一行
    # 每一行是一笔交易
    # 找这个交易的输出具体信息
    def _onefileAllOut(self, filename, rbasedir, wbasedir):
        fr = list(csv.reader(open(rbasedir + '/' + filename, 'r', encoding='UTF-8'), delimiter=';'))
        fw = csv.writer(open(wbasedir + '/' + filename, 'w'), delimiter=';')

        for i in range(0, len(fr)):
            fr[i][6] = json.dumps(self._findTOut(fr[i]))
        fw.writerows(fr)

    def doublelinked(self):
        # 可以直接覆盖写
        rbasedir = self._basedir + "/data"
        wbasedir1 = self._basedir + "/data2"
        wbasedir2 = self._basedir + "/data3"

        years = os.listdir(rbasedir)
        years.sort()
        times = []
        for year in years:
            print(year)
            if not os.path.exists(wbasedir1 + '/' + year):
                os.makedirs(wbasedir1 + '/' + year)

            times = os.listdir(rbasedir + '/' + year)
            times.sort()
            for time in times:
                if not os.path.exists(wbasedir1 + '/' + year + '/' + time):
                    os.makedirs(wbasedir1 + '/' + year + "/" + time)

                # 输入链接
                self._onefileAllIn('result.csv', rbasedir + "/" + year + '/' + time,
                                   wbasedir1 + '/' + year + '/' + time)

        for year in years:
            print(year)
            if not os.path.exists(wbasedir2 + '/' + year):
                os.makedirs(wbasedir2 + '/' + year)
            for time in times:
                if not os.path.exists(wbasedir2 + '/' + year + '/' + time):
                    os.makedirs(wbasedir2 + '/' + year + '/' + time)

                self._onefileAllOut('result.csv', rbasedir + '/' + year + '/' + time,
                                    wbasedir2 + '/' + year + '/' + time)


def writeutxos(utxodict, basedir):
    print("开启线程")
    # 获取锁，用于线程同步
    # self._threadLock.acquire()
    for time, value in utxodict.items():
        f = open(basedir + '/' + time + '/utxo.csv', 'a')
        f.writelines(value)
        f.flush()
        f.close()
    utxodict.clear()
