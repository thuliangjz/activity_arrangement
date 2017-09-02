import re
import codecs
file = codecs.open('raw_qua.txt', 'r', 'utf-8')
content = ' '.join(file.readlines())
pat = re.compile(r'[0-9]{10}')
id_nums = pat.findall(content)
f_out = open('id_nums.txt', 'w')
for num in id_nums:
	f_out.write(num + '\n')