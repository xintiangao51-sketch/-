import re, collections, json
from pathlib import Path

base = Path(r'D:\知识库\00-工作台\inbox\ddc_extract')
out_dir = Path(r'D:\知识库\00-工作台\inbox\ddc_keywords')
out_dir.mkdir(exist_ok=True)

# 1) 主题索引：抽取所有词条（形如"词，页, 页, 页"）
index_text = (base / 'part21_主题索引.txt').read_text(encoding='utf-8')
# 去掉页码分隔
clean = re.sub(r'----- PAGE \d+ -----', '', index_text)
# 词条: 中英文字符+数字+空格+连字符，到第一个数字为止
pattern = re.compile(r'^([A-Za-z\u4e00-\u9fa5][A-Za-z\u4e00-\u9fa5\s\-_/.0-9]{1,80}?)\s*,?\s*([\d\s,、，]+)$', re.MULTILINE)
entries = pattern.findall(clean)
print(f'主题索引抽取条数: {len(entries)}')

# 2) 高频术语(Top 200，过滤PDF噪声)
fulltext = (base / 'ddc_fulltext.txt').read_text(encoding='utf-8')
fulltext_clean = re.sub(r'----- PAGE \d+ -----', '', fulltext)
fulltext_clean = re.sub(r'===== PAGE \d+ =====', '', fulltext_clean)

# 中文 3-6字关键短语
zh_counter = collections.Counter(re.findall(r'[\u4e00-\u9fa5]{2,8}', fulltext_clean))
# 英文专业术语
en_counter = collections.Counter(re.findall(r'[A-Z][A-Za-z0-9\-_]{1,15}', fulltext_clean))

# 提取 PDF 噪声词
noise_words = {'PAGE', 'Available', 'Online', 'Available', 'See', 'Also', 'Chapter', 'Section', 'Example'}
print('\n=== 高频中文术语(Top 100) ===')
zh_results = []
zh_stop = set('我们你们他们这个那个这些那些以及或者但是所以因为如果可以一个一些这种的为了而且不过关于由于按照因此随着通过经过虽然然而可是为与其在于是各自身份人物事项情况事件结果问题所在情况自己不是都是还要会可能只是没有所以之后之前以及已经多少但是'.split())
n=0
for w, c in zh_counter.most_common(2000):
    if w not in zh_stop and c >= 30 and len(w) >= 2 and not re.match(r'^[的了是在有和与或及把被]', w):
        print(f'  {w}: {c}')
        zh_results.append((w, c))
        n+=1
        if n>=100: break

print('\n=== 高频英文专业术语(Top 100) ===')
en_results = []
for w, c in en_counter.most_common(500):
    if c >= 20 and len(w) >= 2 and w not in noise_words and not w.isdigit():
        print(f'  {w}: {c}')
        en_results.append((w, c))
        if len(en_results) >= 100: break

# 保存结果
with open(out_dir / 'zh_keywords.json', 'w', encoding='utf-8') as f:
    json.dump([{'word':w, 'count':c} for w,c in zh_results], f, ensure_ascii=False, indent=2)
with open(out_dir / 'en_keywords.json', 'w', encoding='utf-8') as f:
    json.dump([{'word':w, 'count':c} for w,c in en_results], f, ensure_ascii=False, indent=2)

# 3) 主题索引里所有词条（去重）
index_words = []
for word, pages in entries:
    word_clean = word.strip()
    if 1 < len(word_clean) < 80:
        index_words.append(word_clean)
print(f'\n=== 主题索引总词条数: {len(index_words)} ===')
print('前30条:', index_words[:30])
with open(out_dir / 'index_words.json', 'w', encoding='utf-8') as f:
    json.dump(index_words, f, ensure_ascii=False, indent=2)