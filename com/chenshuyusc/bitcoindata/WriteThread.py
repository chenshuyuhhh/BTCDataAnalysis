import threading

threadLock = threading.Lock()


# 寻找输入的具体值
class WriteThread(threading.Thread):
    def __init__(self, utxodict, basedir, threadLock):
        threading.Thread.__init__(self)
        self._utxodict = utxodict
        self._basedir = basedir
        # self._threadLock = threadLock

    def run(self):
        print("开启线程")
        # 获取锁，用于线程同步
        # self._threadLock.acquire()
        for time, value in self._utxodict.items():
            f = open(self._basedir + '/' + time + '/utxo.csv', 'a')
            f.writelines(value)
            f.flush()
            f.close()
        self._utxodict.clear()
        # 释放锁，开启下一个线程
        # self._threadLock.release()
