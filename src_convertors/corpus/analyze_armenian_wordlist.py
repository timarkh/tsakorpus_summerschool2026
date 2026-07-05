import re
import os
import shutil
from uniparser_eastern_armenian import EasternArmenianAnalyzer


rxDiacritics = re.compile('[՜՞՛]')
rxStems = re.compile('( stem: *)([^\r\n ]+?)( *\n)', flags=re.DOTALL)
rxStemAllomorph = re.compile('([.\\w/_-]+)')
rxSchwaStart = re.compile('\\b([բգդզթժլխծկհձղճմյնշչպջռսվտրցփքֆև])([բգդզթժլխծկհձղճմյնշչպջռսվտրցփքֆև])')
rxSchwaEnd = re.compile('([բգդզթժլխծկհձղճմյնշչպջռսվտրցփքֆև])([բգդզթժլխծկհձղճմյնշչպջռսվտրցփքֆև])\\b')
rxSchwaMiddle = re.compile('([բգդզթժլխծկհձղճմյնշչպջռսվտրցփքֆև])([բգդզթժլխծկհձղճմյնշչպջռսվտրցփքֆև])([բգդզթժլխծկհձղճմյնշչպջռսվտրցփքֆև])')


def repl_stem(m):
    stem = m.group(1)
    stemVars = set(stem.split('//'))
    stemsEw = set()
    for stemVar in stemVars:
        stemEw = stemVar.replace('եւ', 'և')
        if stemEw not in stemVars:
            stemsEw.add(stemEw)
    stemVars |= stemsEw
    stemsIu = set()
    for stemVar in stemVars:
        stemIu = stemVar.replace('իւ', 'յու')
        if stemIu not in stemVars:
            stemsIu.add(stemIu)
    stemVars |= stemsIu

    stemsSchwa = set()
    for i in range(3):
        for stemVar in stemVars:
            stemVarSchwa = rxSchwaStart.sub('\\1ը\\2', stemVar)
            if stemVarSchwa not in stemVars:
                stemsSchwa.add(stemVarSchwa)
            stemVarSchwa = rxSchwaEnd.sub('\\1ը\\2', stemVar)
            if stemVarSchwa not in stemVars:
                stemsSchwa.add(stemVarSchwa)
            stemVarSchwa = rxSchwaMiddle.sub('\\1ը\\2\\3', stemVar)
            if stemVarSchwa not in stemVars:
                stemsSchwa.add(stemVarSchwa)
            stemVarSchwa = rxSchwaMiddle.sub('\\1\\2ը\\3', stemVar)
            if stemVarSchwa not in stemVars:
                stemsSchwa.add(stemVarSchwa)
            stemVarSchwa = rxSchwaEnd.sub('\\1ը\\2', rxSchwaStart.sub('\\1ը\\2', stemVar))
            if stemVarSchwa not in stemVars:
                stemsSchwa.add(stemVarSchwa)
        stemVars |= stemsSchwa
    return '//'.join(s for s in sorted(stemVars))


def repl_stems(m):
    stems = m.group(2)
    stems = rxStemAllomorph.sub(repl_stem, stems)
    return m.group(1) + stems + m.group(3)


def add_spelling_variants(lexemes):
    """
    Ew, schwa etc.
    """
    return rxStems.sub(repl_stems, lexemes)

def collect_lemmata(dirName):
    lemmata = ''
    lexrules = ''
    for fname in os.listdir(dirName):
        if fname.endswith('.txt') and fname.startswith('hye-lexemes'):
            f = open(os.path.join(dirName, fname), 'r', encoding='utf-8-sig')
            lemmata += f.read() + '\n'
            f.close()
        elif fname.endswith('.txt') and fname.startswith('hye-lexrules'):
            f = open(os.path.join(dirName, fname), 'r', encoding='utf-8-sig')
            lexrules += f.read() + '\n'
            f.close()
    lemmataSet = set(re.findall('-lexeme\n(?: [^\r\n]*\n)+', lemmata, flags=re.DOTALL))
    lemmata = '\n'.join(sorted(list(lemmataSet)))
    lemmata = rxDiacritics.sub('', lemmata)
    lemmata = add_spelling_variants(lemmata)
    return lemmata, lexrules


def collect_paradigms(dirName):
    paradigms = ''
    for fname in os.listdir(dirName):
        if fname.endswith('.txt') and fname.startswith('hye-paradigms'):
            with open(os.path.join(dirName, fname), 'r', encoding='utf-8-sig') as fIn:
                paradigms += fIn.read() + '\n'
    return paradigms


def prepare_files():
    """
    Put all the lemmata to lexemes.txt. Put all the lexical
    rules to lexical_rules.txt.
    Put all grammar files to ../uniparser_western_armenian/data/.
    """
    lemmata, lexrules = collect_lemmata('.')
    paradigms = collect_paradigms('.')
    with open('uniparser_eastern_armenian/data/lexemes.txt', 'w', encoding='utf-8') as fOutLemmata:
        fOutLemmata.write(lemmata)
    with open('uniparser_eastern_armenian/data/paradigms.txt', 'w', encoding='utf-8') as fOutParadigms:
        fOutParadigms.write(paradigms)
    fOutLexrules = open('uniparser_eastern_armenian/data/lex_rules.txt', 'w', encoding='utf-8')
    fOutLexrules.write(lexrules)
    fOutLexrules.close()
    shutil.copy2('bad_analyses.txt', 'uniparser_eastern_armenian/data/')
    shutil.copy2('armenian_disambiguation.cg3', 'uniparser_eastern_armenian/data/')


def process_diacritics(a, fnameBase='wordlist'):
    """
    Find unanalyzed words that contain a schwa inside and try analyzing them
    without the schwa. Add the results to the list of analyzed words.
    """
    rxDia = re.compile('^([\\w\'՛՚]+)[՜՞՛](\\w+)$')
    unanalyzedDia = []
    norm2dia = {}
    freqDict = {}
    with open(fnameBase + '_unanalyzed.txt', 'r', encoding='utf-8') as fIn:
        for word in fIn:
            word = word.strip()
            if rxDia.search(word) is not None:
                unanalyzedDia.append(word)
    with open(fnameBase + '.csv', 'r', encoding='utf-8') as fIn:
        for line in fIn:
            word, freq = line.strip().split('\t')
            freqDict[word] = freq
    with open(fnameBase + '_dia.csv', 'w', encoding='utf-8') as fOut:
        for word in unanalyzedDia:
            wordNorm = rxDia.sub('\\1\\2', word)
            if wordNorm not in norm2dia:
                norm2dia[wordNorm] = [word]
                fOut.write(wordNorm
                           + '\t' + freqDict[word] + '\n')
            else:
                norm2dia[wordNorm].append(word)
    print('Processing diacriticized words...')
    a.analyze_wordlist(freqListFile=fnameBase + '_dia.csv',
                       parsedFile=fnameBase + '_analyzed_dia.txt',
                       unparsedFile=fnameBase + '_unanalyzed_dia.txt',
                       verbose=True)
    analyzedDia = set()
    with open(fnameBase + '_analyzed_dia.txt', 'r', encoding='utf-8') as fIn:
        lines = '\n'
        for line in fIn:
            m = re.search('^(.*>)([^<>\r\n]+)</w>', line)
            if m is None:
                continue
            wordNorm = m.group(2)
            for word in norm2dia[wordNorm]:
                analyzedDia.add(word)
                lines += m.group(1) + word + '</w>\n'
    with open(fnameBase + '_analyzed.txt', 'a', encoding='utf-8') as fOut:
        fOut.write(lines)
    lines = []
    with open(fnameBase + '_unanalyzed.txt', 'r', encoding='utf-8') as fIn:
        for line in fIn:
            line = line.strip()
            if line not in analyzedDia:
                lines.append(line)
    with open(fnameBase + '_unanalyzed.txt', 'w', encoding='utf-8') as fOut:
        fOut.write('\n'.join(lines))


def process_whitespaces():
    """
    Remove whitespaces and apostrophes in the parts attribute (for կը).
    """
    rxRemove = re.compile('[\'՚՛ ]+')
    with open('wordlist_analyzed.txt', 'r', encoding='utf-8') as fIn:
        text = fIn.read()
    text = re.sub('\\bparts="([^"\r\n]+)"', lambda m: 'parts="' + rxRemove.sub('', m.group(1)) + '"', text)
    with open('wordlist_analyzed.txt', 'w', encoding='utf-8') as fOut:
        fOut.write(text)


def add_freqs():
    """
    Add frequencies to the unanalyzed word list.
    """
    unparsed = set()
    with open('wordlist_unanalyzed.txt', 'r', encoding='utf-8') as fIn:
        for line in fIn:
            unparsed.add(line.strip())
    freqs = {}
    with open('wordlist.csv', 'r', encoding='utf-8') as fIn:
        for line in fIn:
            if len(line) <= 2 or '\t' not in line:
                continue
            word, freq = line.strip().split('\t')
            freqs[word] = int(freq)
    with open('wordlist_unanalyzed_freq.csv', 'w', encoding='utf-8') as fOut:
        for word in sorted(freqs, key=lambda w: (-freqs[w], w)):
            if word in unparsed:
                fOut.write(word + '\t' + str(freqs[word]) + '\n')


def parse_wordlists():
    """
    Analyze wordlists/wordlist.csv.
    """
    a = EasternArmenianAnalyzer()
    a.analyze_wordlist(parsedFile='wordlist_analyzed.txt',
                       unparsedFile='wordlist_unanalyzed.txt')
    process_diacritics(a)
    process_whitespaces()


if __name__ == '__main__':
    prepare_files()
    parse_wordlists()
