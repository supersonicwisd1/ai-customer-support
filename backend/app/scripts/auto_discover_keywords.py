import os
import glob
import json
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy

ARCHIVE_DIR = os.path.join(os.path.dirname(__file__), '../../archive')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '../../auto_discovered_keywords.json')

# Load all archived .txt files
all_texts = []
for txt_file in glob.glob(os.path.join(ARCHIVE_DIR, '*.txt')):
    with open(txt_file, 'r', encoding='utf-8') as f:
        all_texts.append(f.read())

# TF-IDF keyword extraction
vectorizer = TfidfVectorizer(max_features=100, stop_words='english', ngram_range=(1,2))
X = vectorizer.fit_transform(all_texts)
feature_array = vectorizer.get_feature_names_out()
tfidf_sorting = X.toarray().sum(axis=0).argsort()[::-1]
top_keywords = [feature_array[i] for i in tfidf_sorting[:30]]

# spaCy NER extraction
nlp = spacy.load('en_core_web_sm')
entity_counter = Counter()
for text in all_texts:
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in {'ORG', 'PRODUCT', 'PERSON', 'GPE', 'EVENT', 'LAW'}:
            entity_counter[ent.text.strip()] += 1

top_entities = [ent for ent, _ in entity_counter.most_common(30)]

# Output results
result = {
    'tfidf_keywords': top_keywords,
    'named_entities': top_entities
}

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)

print(f"Auto-discovered keywords and entities saved to {OUTPUT_FILE}") 