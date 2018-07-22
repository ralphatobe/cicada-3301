import os
import json

import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

def find_blob(indices, x, y, x_sum, y_sum):
  if (x, y) in indices:
    x_sum += x
    y_sum += y
    indices.remove((x, y))
    indices, x_sum, y_sum = find_blob(indices, x + 1, y, x_sum, y_sum)
    indices, x_sum, y_sum = find_blob(indices, x, y + 1, x_sum, y_sum)
    indices, x_sum, y_sum = find_blob(indices, x - 1, y, x_sum, y_sum)
    indices, x_sum, y_sum = find_blob(indices, x, y - 1, x_sum, y_sum)
  return indices, x_sum, y_sum

# for i in xrange(6):
#     plt.subplot(2,3,i+1),plt.imshow(images[i],'gray')
#     plt.title(titles[i])
#     plt.xticks([]),plt.yticks([])

kernel_1 = np.ones((3, 3), np.uint8)
kernel_2 = np.ones((5, 5), np.uint8)


# iterate over all pages
for page_root, dirs, page_files in os.walk('2014onion7'):
  for page_file in page_files:
    if page_file[-4:] == '.jpg':
      print(page_file)

      # read and binarize page
      page = cv.imread(os.path.join(page_root, page_file), 0)
      ret, page = cv.threshold(page, 127, 255, cv.THRESH_BINARY)
      page = 255 - page

      hit_img = np.zeros_like(page, dtype=float)

      if 'read_page' in locals():
        del read_page

      # page_char = page/4
      # iterate over all characters
      for root, dirs, files in os.walk('Cropped Vocabulary'):
        for file in files:
          # print(file)
          # read and binarize character
          img = cv.imread(os.path.join(root, file), 0)
          ret, img = cv.threshold(img, 127, 255, cv.THRESH_BINARY)
          img = 255 - img
          # extract character
          char, _ = file.split('.')
          # chars = chars.split('-')
          
          # erode the character to make sure it matches on the page
          img_erode_1 = cv.erode(img, kernel_1)
          # create a character outline for the hit or miss filter
          img_erode_2 = cv.dilate(img, kernel_2) - cv.dilate(img, kernel_1)
          # run hit or miss filter
          page_erode_1 = cv.erode(page, img_erode_1, borderValue=0)
          page_erode_2 = cv.erode(255 - page, img_erode_2, borderValue=0)
          page_erode = np.logical_and(page_erode_1, page_erode_2)
          page_erode = page_erode.astype(np.uint8) * 255

          # check if character is present in image
          if sum(sum(page_erode)) > 0:

            kernel = np.fliplr(np.flipud(img))
            # page_char = page/2 + cv.dilate(page_erode, kernel)/2

            char_indices = np.argwhere(page_erode)
            data = []
            for coords in char_indices.tolist():
              coords.append(char)
              data.append(tuple(coords))
            dtype = [('y', int), ('x', int), ('char', object)]
            found_chars = np.array(data, dtype=dtype) 
            # print(found_chars)

            if 'read_page' in locals():
              read_page += cv.dilate(page_erode, kernel)/2
              all_chars = np.concatenate((all_chars, found_chars))
            else:
              read_page = cv.dilate(page_erode, kernel)/2
              all_chars = found_chars

            hit_img += read_page
              
      # print(all_chars)
      # if page_file == '57.jpg':
      # plt.imshow(hit_img > 0, 'gray')
      # plt.show()

      char2idx = {}
      for x, y, char in all_chars:
        if char in char2idx.keys():
          char2idx[char].append((x, y))
        else:
          char2idx[char] = [(x, y)]

      char2centers = {}
      for char, indices in char2idx.items():
        # print("Character:", char)
        while indices:
          x, y = indices[0]
          # print("Indices:", indices)
          num_idx = len(indices)
          indices, x_sum, y_sum = find_blob(indices, x, y, 0, 0)
          blob_size = num_idx - len(indices)
          x = x_sum / blob_size
          y = y_sum / blob_size
          # print("Centroid:", x, y)

          if char in char2centers.keys():
            char2centers[char].append((x, y))
          else:
            char2centers[char] = [(x, y)]

      if '13_dots' in char2centers.keys():
        img = cv.imread(os.path.join('Cropped Vocabulary', '13_dots.png'), 0)
        height, width = img.shape
        remove = []
        for y, x in char2centers['13_dots']:
          for j, i in char2centers['1_dot']:
            if i < x + width/2 and i > x - width/2 and \
               j < y + height/2 and j > y - height/2:
               remove.append((j, i))

          # print(remove)
          for y, x in remove:
            char2centers['1_dot'].remove((y, x))
          remove = []

      if '4_dots' in char2centers.keys():
        img = cv.imread(os.path.join('Cropped Vocabulary', '4_dots.png'), 0)
        height, width = img.shape
        remove = []
        for y, x in char2centers['4_dots']:
          for j, i in char2centers['1_dot']:
            if i < x + width/2 and i > x - width/2 and \
               j < y + height/2 and j > y - height/2:
               remove.append((j, i))

          # print(remove)
          for y, x in remove:
            char2centers['1_dot'].remove((y, x))
          remove = []

      if 'Y' in char2centers.keys():
        img = cv.imread(os.path.join('Cropped Vocabulary', 'Y.png'), 0)
        height, width = img.shape
        remove = []
        for y, x in char2centers['Y']:
          for j, i in char2centers['U']:
            if i < x + width/2 and i > x - width/2 and \
               j < y + height/2 and j > y - height/2:
               remove.append((j, i))

          # print(remove)
          for y, x in remove:
            char2centers['U'].remove((y, x))
          remove = []

      data = []
      for key, values in char2centers.items():
        for x, y in values:
          data.append((x, y, key))

      ordered_chars = np.array(data, dtype=dtype) 

      transcript = np.sort(ordered_chars, order=['y', 'x'])

      min_y = transcript[0][0]
      max_y = transcript[-1][0]

      # print(max_y - min_y)
      # print((max_y - min_y)/200)

      num_lines = np.ceil((max_y - min_y)/200) + 1

      bins = np.linspace(min_y, max_y, num_lines)

      # print(bins)

      bin_num = 0
      for idx, letter in enumerate(transcript):
        # print(letter)
        # print(bins[bin_num])
        y, x, char = letter
        while y < bins[bin_num] - 100 or  y > bins[bin_num] + 100:
          # print("New line")
          bin_num += 1
          # print(bins[bin_num])
        
        transcript[idx] = (bins[bin_num], x, char)

      idx_transcript = np.sort(transcript, order=['y', 'x'])

      # print(idx_transcript)

      transcript = []
      for y, x, char in idx_transcript:
        if char == '1_dot':
          transcript.append(" ")
        elif char == '4_dots':
          transcript.append(".")
        elif char == '13_dots':
          transcript.append(";")
        else:
          transcript.append(char)

      filepath = os.path.join('transcripts', page_file[:-4] + '.json')
      if not(os.path.exists('transcripts')):
        os.makedirs('transcripts')

      with open(filepath, 'w') as f:
        json.dump(transcript, f)

      # print(len(transcript))
