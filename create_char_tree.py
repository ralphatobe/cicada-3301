
primus = ['F','U','TH','O','R','C-K','G','W','H','N','I','J','EO','P','X','S-Z','T','B','E','M','L','NG-ING','OE','D','A','AE','Y','IA-IO','EA']

char_tree = {}
for cipher_item in primus:
  for cipher_char in cipher_item.split('-'):
    head = cipher_char[0]
    if len(cipher_char) > 1:
      tail = cipher_char[1:]
      if head in char_tree.keys():
        char_tree[head].append(tail)
      else:
        char_tree[head] = [tail]
    else:
      if head not in char_tree.keys():
        char_tree[head] = []


print(char_tree)