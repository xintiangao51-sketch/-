import os
root = r'D:/知识库'
keys = ['哈密国源','国源','综合能源集控','集控服务中心','煤电公司综合']
for dirpath, dirnames, filenames in os.walk(root):
    p = dirpath.replace('\\', '/')
    if any(k in p for k in keys):
        print('\nDIR', p)
        for f in filenames[:100]:
            print('  ', f)
        if len(filenames) > 100:
            print('  ...', len(filenames), 'files')
    else:
        hits = [f for f in filenames if any(k in f for k in keys)]
        if hits:
            print('\nDIR', p)
            for f in hits:
                print('  ', f)
