import copy


def splitter(transcript, splitters=[' ', ';', '.']):
  word = []
  for char in transcript:
    if char in splitters:
      yield word
      word = []
    else:
      word.append(char)


def variant_joiner(chars):
  word_variants = [[]]
  for char in chars:
    if '-' in char:
      new_variants = copy.deepcopy(word_variants)
      char_1, char_2 = char.split('-')
      for word_variant in word_variants:
        word_variant.append(char_1)
      for word_variant in new_variants:
        word_variant.append(char_2)
      word_variants.extend(new_variants)
    else:
      for word_variant in word_variants:
        word_variant.append(char)
  for word_variant in word_variants:
    yield ''.join(word_variant)