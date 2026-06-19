# -*- coding: utf-8 -*-
"""测试新疆造价爬虫连接"""
import sys, os, yaml, requests
sys.path.insert(0, '.')

from crawler.zjt import ZJTCrawler
from storage.db import Database

# 加载配置
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 初始化数据库
db = Database(config['database']['path'])
print(f'✅ 数据库初始化成功: {config["database"]["path"]}')

# 测试4个爬虫连接
for source in config['sources']:
    if not source.get('enabled', True):
        print(f'⏭ {source["name"]}: disabled')
        continue
    
    name = source['name']
    url = source['url']
    print(f'\n--- {name} ---')
    print(f'   URL: {url}')
    
    # 测试连接
    try:
        r = requests.get(url, timeout=15, headers={'User-Agent': config['crawl']['user_agent']})
        print(f'   HTTP: {r.status_code} | 长度: {len(r.text)} 字符')
        if r.status_code == 200:
            print(f'   ✅ 可连接')
        else:
            print(f'   ⚠ 非200状态码')
    except requests.ConnectionError as e:
        print(f'   ❌ 连接失败: {e}')
    except requests.Timeout:
        print(f'   ❌ 超时')
    except Exception as e:
        print(f'   ❌ 异常: {e}')

print('\n--- 测试完成 ---')
