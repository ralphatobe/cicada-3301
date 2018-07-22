import os
import json

import matplotlib.pyplot as plt

from collections import Counter
from utils import splitter, variant_joiner


CHAPTERS = [[0, 1, 2], [3, 4, 5, 6, 7], [8, 9, 10, 11, 12, 13, 14], [15, 16, 17, 18, 19, 20, 21, 22], [23, 24, 25, 26], [27, 28, 29, 30, 31, 32], [33, 34, 35, 36, 37, 38, 39], [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55], [56], [57]]
CHAR_BY_FREQ = 'ETAOINSRHDLUCMFYWGPBVKXQJZ'

for chapter in CHAPTERS:
  unigrams = Counter()
  for page in chapter:
    print("processing page", page)
    chars = []
    with open(os.path.join('transcripts', str(page) + '.json')) as f:
      data = json.load(f)
      for char in data:
        if char not in [' ', '.', ';']:
          chars.extend(set(char) - set('-'))
    unigrams.update(chars)
  # print(unigrams)
  alphabet, alphabet_counts = zip(*unigrams.most_common())
  # plt.bar(range(len(alphabet_counts)), alphabet_counts)
  # plt.xticks(range(len(alphabet)), alphabet)
  # plt.show()
  char_mapping = {}
  for key, value in zip(alphabet, list(CHAR_BY_FREQ)):
    char_mapping[key] = value
  # print(char_mapping)

  page = chapter[0]
  print("demoing page", page)
  words = []
  with open(os.path.join('transcripts', str(page) + '.json')) as f:
    data = json.load(f)
    word_chars = list(splitter(data))
    for char_set in word_chars:
      word_variants = list(variant_joiner(char_set))
      words.extend(word_variants)
    print(words)
    new_words = []
    for word in words:
      new_word = []
      for char in word:
        new_word.append(char_mapping[char])
      new_words.append(''.join(new_word))
    print(new_words)