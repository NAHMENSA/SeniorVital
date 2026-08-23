import json
import re

with open(r'E:\SeniorVital-master\data\processed\chunks\all_chunks.json', 'r', encoding='utf-8') as f:
    chunks = json.load(f)

print(f'Total chunks: {len(chunks)}')

# Group by macrodomain
domains = {}
for c in chunks:
    d = c['macrodomain']
    if d not in domains:
        domains[d] = []
    domains[d].append(c)

for d in sorted(domains.keys()):
    names = sorted(set(c['document_name'] for c in domains[d]))
    print(f'\n{"="*70}')
    print(f'DOMAIN {d} - {domains[d][0]["macrodomain_name"]} ({len(domains[d])} chunks)')
    print(f'{"="*70}')
    for n in names:
        c_list = [c for c in domains[d] if c['document_name'] == n]
        ids = [c['chunk_id'] for c in c_list]
        print(f'\n  [{n}] ({len(c_list)} chunks)')
        for c in c_list:
            print(f'    {c["chunk_id"]} | idx={c["chunk_index"]} | words={c["word_count"]} | path={c["section_path"]} | kw={c["keywords"]} | pathology={c["pathology"]}')
            print(f'      content(200): {c["content"][:200]}')
            print()

# Chunks with conditions
print('\n' + '='*70)
print('CHUNKS MENTIONING SPECIFIC CONDITIONS')
print('='*70)
for c in chunks:
    text = c.get('content','').lower()
    pathol = (c.get('pathology','') or '').lower()
    conditions = []
    if 'diabetes' in text or 'diabetes' in pathol: conditions.append('diabetes')
    if 'osteoporosis' in text or 'osteoporosis' in pathol: conditions.append('osteoporosis')
    if 'sarcopenia' in text or 'sarcopenia' in pathol: conditions.append('sarcopenia')
    if 'knee' in text or 'rodilla' in text or 'femoropatelar' in text: conditions.append('knee-related')
    if 'hipertens' in text or 'hipertensión' in text or 'presión arterial' in text: conditions.append('hypertension')
    if 'artritis' in text or 'artrosis' in text: conditions.append('arthritis/osteoarthritis')
    if 'dolor lumbar' in text or 'lumbar' in text: conditions.append('low-back')
    if 'depresión' in text or 'ansiedad' in text: conditions.append('depression/anxiety')
    if 'caída' in text or 'caídas' in text: conditions.append('fall-prevention')
    if conditions:
        print(f'  {c["chunk_id"]} | {c["macrodomain"]} | {conditions} | {c["document_name"][:50]}')

# Multi-topic chunks
print('\n' + '='*70)
print('MULTI-TOPIC CHUNKS (keywords covering multiple domains)')
print('='*70)
for c in chunks:
    kw = c.get('keywords', [])
    if len(kw) >= 3:
        print(f'  {c["chunk_id"]} | {c["macrodomain"]} | kw={kw} | {c["document_name"][:50]}')
        print(f'    {c["content"][:150]}')
        print()

# Short chunks
print('='*70)
print('SHORT CHUNKS (< 50 words)')
print('='*70)
for c in chunks:
    if c['word_count'] < 50:
        print(f'  {c["chunk_id"]} | {c["macrodomain"]} | {c["word_count"]}w | {c["document_name"][:50]}')
        print(f'    {c["content"][:150]}')
        print()

# Outdoor exercise
print('='*70)
print('OUTDOOR EXERCISE CHUNKS')
print('='*70)
outdoor_kw = ['aire libre', 'outdoor', 'exterior', 'senderismo', 'ciclovía', 'paseo', 'parque']
for c in chunks:
    text = c.get('content','').lower()
    if any(w in text for w in outdoor_kw):
        print(f'  {c["chunk_id"]} | {c["macrodomain"]} | {c["document_name"][:50]}')
        print(f'    {c["content"][:150]}')
        print()

# Home adaptation
print('='*70)
print('HOME ADAPTATION CHUNKS')
print('='*70)
home_kw = ['domicilio', 'en casa', 'hogar', 'adaptación del hogar', 'ejercicio en casa', 'manual_ejercicio_persona_mayor_domicilio']
for c in chunks:
    text = c.get('content','').lower()
    doc = c.get('document_name','').lower()
    if any(w in text for w in home_kw) or any(w in doc for w in home_kw):
        print(f'  {c["chunk_id"]} | {c["macrodomain"]} | {c["document_name"][:50]}')
        print(f'    {c["content"][:150]}')
        print()

# Nutrition specifics
print('='*70)
print('NUTRITION SPECIFICS (macrodomain E + other)')
print('='*70)
nutr_kw = ['calcio', 'vitamina d', 'proteína', 'proteínas', 'omega', 'fibra', 'sodio', 'nutrición', 'alimentación', 'dieta', 'calorías']
for c in chunks:
    text = c.get('content','').lower()
    if any(w in text for w in nutr_kw) and c['macrodomain'] == 'E':
        print(f'  {c["chunk_id"]} | {c["macrodomain"]} | {c["document_name"][:50]}')
        print(f'    {c["content"][:150]}')
        print()

# Cognitive exercises
print('='*70)
print('COGNITIVE EXERCISE CHUNKS')
print('='*70)
cog_kw = ['cognitiv', 'memoria', 'estimulación cognitiva', 'ejercicios para estimular memoria']
for c in chunks:
    text = c.get('content','').lower()
    if any(w in text for w in cog_kw):
        print(f'  {c["chunk_id"]} | {c["macrodomain"]} | {c["document_name"][:50]}')
        print(f'    {c["content"][:150]}')
        print()

# Summary stats
print('\n' + '='*70)
print('SUMMARY STATISTICS')
print('='*70)
for d in sorted(domains.keys()):
    d_chunks = domains[d]
    wc = [c['word_count'] for c in d_chunks]
    print(f'  Domain {d}: {len(d_chunks)} chunks, avg {sum(wc)//len(wc)} words, min={min(wc)}, max={max(wc)}')
    print(f'    Documents: {sorted(set(c["document_name"] for c in d_chunks))}')

# Multi-topic by pathology
print('\n' + '='*70)
print('CHUNKS WITH PATHOLOGY TAG')
print('='*70)
for c in chunks:
    if c.get('pathology'):
        print(f'  {c["chunk_id"]} | {c["macrodomain"]} | pathology={c["pathology"]} | {c["document_name"][:50]}')
