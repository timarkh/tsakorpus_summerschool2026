# A shell script used to prepare the corpus files for indexing.
# Generates word lists, annotates them, runs a convertor and puts
# the resulting JSON files to the appropriate folder.
START_TIME="$(date -u +%s)"
cd src_convertors/corpus
python3 concordancer.py
echo "Word list generated."

rm -rf uniparser-grammar-eastern-armenian
git clone https://github.com/timarkh/uniparser-grammar-eastern-armenian.git
echo "Grammar repository cloned."
cd uniparser-grammar-eastern-armenian
cp armenian_disambiguation.cg3 ..
mv ../wordlist.csv wordlist.csv
cp ../analyze_armenian_wordlist.py .
echo "Source files moved."
python3 analyze_armenian_wordlist.py
mv analyzed.txt ../wordlist.csv-parsed.txt
mv unanalyzed.txt ../wordlist.csv-unparsed.txt
echo "Word list analyzed."
cd ..
rm -rf uniparser-grammar-eastern-armenian
cd ..

# Conversion to Tsakorpus JSON
python3 txt2json.py
echo "Source conversion ready."
rm corpus/wordlist.csv-parsed.txt
rm corpus/armenian_disambiguation.cg3
rm -rf ../corpus/armenian_summerschool2026
mkdir -p ../corpus/armenian_summerschool2026
mv corpus/json_disamb ../corpus/armenian_summerschool2026
rm -rf corpus/cg
rm -rf corpus/cg_disamb
rm -rf corpus/json

echo "The JSON files are prepared, moved to corpus/armenian_artsakh_interviews and ready for indexing. They will be indexed in the Elasticsearch database. This may take some time."
cd ../indexator
python3.9 indexator.py -y y

END_TIME="$(date -u +%s)"
ELAPSED_TIME="$(($END_TIME-$START_TIME))"
echo "Corpus files prepared in $ELAPSED_TIME seconds, finishing now."