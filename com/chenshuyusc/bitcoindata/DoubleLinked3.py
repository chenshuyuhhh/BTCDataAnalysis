import json
import redis
import csv
import os
from multiprocessing import Process
import logging

csv.field_size_limit(500 * 1024 * 1024)

logging.basicConfig(level=logging.DEBUG, filename='linkaddr.log')


# 根据原始交易文件获得信息
class DoubleLinked:
    def __init__(self, basedir):
        # redis 连接池
        # txid#index   addrv
        pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
        self._r = redis.Redis(connection_pool=pool)
        self._ruxto = redis.Redis(connection_pool=pool)

        self._basedir = basedir

        self._lines = []
        self._wfile = ""
        # time-list
        self._utxodict = {}
        self._rfile = ""

        self._processes = []

    def _findTOut(self, line):
        txid = line[8]  # 交易 "txhash"
        vouts = json.loads(line[6])  # 交易的输出 'vout'

        for i in range(0, len(vouts)):
            key = txid + '#' + str(i)

            if self._ruxto.exists(key):
                spend = self._ruxto.get(key).split('#')
                # spend_time  # spend_tx
                vouts[i]['spend_time'] = spend[0]
                vouts[i]['spend_tx'] = spend[1]

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
                logging.info('not exist')
                logging.info(in_txid)
                logging.info(txhash)
                # self.revlines.add(in_txid)
                # 没找到，存着后续找
                # 暂时侥幸心里，不管
                continue

            # 在redis数据库中根据txid和num找输入的具体值
            addrv = self._r.get(key).split('#')  # 输入的地址和金额

            # 将该交易的输入信息中的地址和金额补充完整
            vins[j]["address"] = addrv[0]
            vins[j]["value"] = float(addrv[1])

            #    txhashnum, spend_time#spend_tx#time
            if addrv[2] in self._utxodict:
                self._utxodict[addrv[2]].append(key + ',' + str(line[7]) + '#' + txhash + '\n')
            else:
                self._utxodict[addrv[2]] = [key + ',' + str(line[7]) + '#' + txhash + '\n']

            # 从redis中删除
            self._r.delete(key)

        return vins

    def _vout2redis(self, txhash, vouts, time):
        for i in range(0, len(vouts)):
            self._r.set(txhash + '#' + str(i),
                        vouts[i]['address'] + '#' + str(vouts[i]['value']) + '#' + str(time))  # line[8] 交易哈希

    def _lines2In(self):

        for i in range(0, len(self._lines)):
            # 做输入的链接，并更新交易的输入
            self._lines[i][5] = json.dumps(self._findTIn(self._lines[i]))  # vin

        f = open(self._wfile, 'w')
        fw = csv.writer(f, delimiter=';')
        fw.writerows(self._lines)
        f.close()

    # 根据文件filename，遍历每一行
    # 每一行是一笔交易
    # 找这个交易的输出具体信息
    def _onefileAllOut(self, f1, f2, basedir):
        fr = list(csv.reader(open(basedir + '/' + f1, 'r', encoding='UTF-8'), delimiter=';'))
        fw = csv.writer(open(basedir + '/' + f2, 'w'), delimiter=';')

        for i in range(0, len(fr)):
            fr[i][6] = json.dumps(self._findTOut(fr[i]))
        fw.writerows(fr)

    def _getfilenames(self):

        files = []

        years = os.listdir(self._basedir)
        years.sort()

        for year in years:
            # 建目录
            times = os.listdir(self._basedir + '/' + year)
            times.sort()
            for time in times:
                # 存文件
                files.append(year + '/' + time)

        return files

    def _writeutxo(self):
        for time, value in self._utxodict.items():
            f = open(self._basedir + '/' + time + '/utxo.csv', 'a')
            f.writelines(value)
            f.flush()
            f.close()
        self._utxodict.clear()

    def _allFileIn(self, absdirs):
        # 先把第一个存起来
        self._lines = list(csv.reader(open(self._basedir + '/' + absdirs[0] + '/' + 'result.csv', 'r'), delimiter=';'))
        for line in self._lines:
            self._vout2redis(txhash=line[8], vouts=json.loads(line[6]), time=absdirs[0])

        self._wfile = self._basedir + '/' + absdirs[0] + '/' + 'result1.csv'

        # 后续就是循环，当前存进redis，上一个做输入链接
        i = 0
        for absdir in absdirs[1:]:
            logging.info(absdir)
            i = i + 1
            # 存进去
            fr = list(csv.reader(open(self._basedir + '/' + absdir + '/' + 'result.csv', 'r'), delimiter=';'))
            for line in fr:
                self._vout2redis(txhash=line[8], vouts=json.loads(line[6]), time=absdir)

            self._lines2In()

            # 下一轮要找的
            self._lines = fr
            self._wfile = self._basedir + '/' + absdir + '/' + 'result1.csv'

            if len(self._utxodict) > 400 and i > 10:  # 存utxo
                i = 0
                utxodict = self._utxodict
                self._utxodict.clear()
                p = Process(target=writeutxos, args=(utxodict, self._basedir))
                self._processes.append(p)
                p.start()
                logging.info("开启线程后")

        # 最后一个文件单独找输入
        self._lines2In()

        utxodict = self._utxodict
        self._utxodict.clear()
        p = Process(target=writeutxos, args=(utxodict, self._basedir))
        self._processes.append(p)
        p.start()

        # 等待所有线程完成
        for t in self._processes:
            t.join()
        logging.info("退出主进程")

    def deluxto(self):
        # 得到文件列表
        absdirs = self._getfilenames()

        for absdir in absdirs:
            if os.path.exists(self._basedir + '/' + absdir + '/' + 'utxo.csv'):
                os.remove(self._basedir + '/' + absdir + '/' + 'utxo.csv')
                print(absdir)

    def doublelinked(self):
        # 得到文件列表
        absdirs = self._getfilenames()

        self._allFileIn(absdirs)

        # 输出链接
        for absdir in absdirs:
            logging.info(absdir)
            # 读入utxo
            if os.path.exists(self._basedir + '/' + absdir + '/' + 'utxo.csv'):
                rfile = csv.reader(open(self._basedir + '/' + absdir + '/' + 'utxo.csv', 'r'))

                for line in rfile:
                    self._ruxto.set(line[0], line[1])
                self._onefileAllOut('result.csv', 'result2.csv', self._basedir + '/' + absdir)


def writeutxos(utxodict, basedir):
    logging.info("开启进程")
    # 获取锁，用于线程同步
    # self._threadLock.acquire()
    for time, value in utxodict.items():
        f = open(basedir + '/' + time + '/utxo.csv', 'a')
        f.writelines(value)
        f.flush()
        f.close()
    utxodict.clear()
    logging.info("退出进程")
