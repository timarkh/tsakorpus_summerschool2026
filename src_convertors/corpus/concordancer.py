import re
import os
rxWords = re.compile('\\b[Ա-Ֆ՜՞-և][Ա-Ֆ՜՞-և-]*[Ա-Ֆ՜՞-և]\\b|\\b[Ա-Ֆ՜՞-և]\\b')
rxPunct = re.compile('[ՙ՚՜՛՝՞՟։֊.,(){}\\[\\]:;?!"«»]')


def process_file(fpath, fname, dictConc):
    f = open(os.path.join(fpath, fname), 'r', encoding='utf-8-sig')
    text = f.read()
    f.close()
    words = rxWords.findall(text)
    for word in words:
        word = word.lower()
        word = rxPunct.sub('', word)
        if len(word) <= 0:
            continue
        try:
            dictConc[word] += 1
        except KeyError:
            dictConc[word] = 1
        if '-' in word:
            parts = word.split('-')
            for iPart in range(len(parts)):
                part = parts[iPart]
                if iPart != len(parts) - 1:
                    part += '-'
                else:
                    part = '-' + part
                try:
                    dictConc[part] += 1
                except KeyError:
                    dictConc[part] = 1
    return len(words)


def write_conc(dictConc, fname):
    f = open(fname, 'w', encoding='utf-8-sig')
    for word in sorted(dictConc, key=lambda w: -dictConc[w]):
        f.write(word + '\t' + str(dictConc[word]) + '\n')
    f.close()


conc = {}
nWords = 0
for root, dirs, files in os.walk('./txt'):
    print(root)
    for fname in files:
        if not fname.endswith('.txt') or re.search('meta|parsed|concord|_uncleaned', fname) is not None:
            continue
        if '_uncleaned' in root:
            continue
        nWords += process_file(root, fname, conc)
write_conc(conc, 'wordlist.csv')
print('Corpus size: ' + str(nWords) + ' words.')
