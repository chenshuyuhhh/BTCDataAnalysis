

f = open('/Users/chenshuyu/Documents/blockChain/BTC_deanonymization_model/result.csv', 'r', encoding='UTF-8-sig')
fw = open('/Users/chenshuyu/Documents/blockChain/BTC_deanonymization_model/result2.csv', 'w')
new_lines = []
for line in f:
    line = line.replace("\'", "\"")
    fw.write(line)