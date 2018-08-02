import os
import json
import matplotlib

import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt


def priotize_chars(high_priority, low_priority, char2centers):
  if high_priority in char2centers.keys() and low_priority in char2centers.keys():
    # read higher priority image and extract character size
    img = cv.imread(os.path.join('cropped vocabulary', high_priority + '.png'), 0)
    height, width = img.shape
    remove = []
    for y, x in char2centers[high_priority]:
      for j, i in char2centers[low_priority]:
        # if characters overlap, collect lower priority character index
        if i < x + width/2 and i > x - width/2 and \
           j < y + height/2 and j > y - height/2:
           remove.append((j, i))
      # remove targeted low priority characters
      for y, x in remove:
        char2centers[low_priority].remove((y, x))
      remove = []
  return char2centers


def find_blob(indices, x, y, x_sum, y_sum):
  # recursively find centroid of connected hit pixels
  if (x, y) in indices:
    x_sum += x
    y_sum += y
    indices.remove((x, y))
    indices, x_sum, y_sum = find_blob(indices, x + 1, y, x_sum, y_sum)
    indices, x_sum, y_sum = find_blob(indices, x, y + 1, x_sum, y_sum)
    indices, x_sum, y_sum = find_blob(indices, x - 1, y, x_sum, y_sum)
    indices, x_sum, y_sum = find_blob(indices, x, y - 1, x_sum, y_sum)
  return indices, x_sum, y_sum


def k_means(points, k):
  centroids = np.random.choice(np.unique(points), size=(k, 1), replace=False)
  centroids = np.sort(centroids, 0)

  old_labels = np.ones((k, points.shape[0])) * np.inf
  count = 0
  while True:
    count += 1
    # print(np.tile(points, (k, 1)) - centroids)
    distances = np.abs(np.tile(points, (k, 1)) - centroids)
    # print(points)
    print(centroids)
    print(distances)
    # print(distances)
    new_labels = np.argmin(distances, 0)
    if np.all(new_labels == old_labels) or count > 100:
      # print(count)
      break
    for i in range(k):
      centroids[i] = np.mean(points[new_labels == i])
      # centroids = np.sort(centroids)
    old_labels = new_labels
  # centroids = np.sort(centroids)
  return centroids, new_labels


def avg_silhouette(points, labels, k):
  silhouettes = np.ones_like(points) * np.inf
  for i in range(points.shape[0]):
    # print(points[i])
    distances = np.square(points - points[i])
    wss = distances[labels == labels[i]]
    a = np.sum(wss)/(wss.shape[0] - 1)
    # print(a)
    cluster_dists = np.zeros((k - 1))
    other_clusters = list(range(k))
    other_clusters.remove(labels[i])
    for n, label in enumerate(other_clusters):
      oss = distances[labels == label]
      cluster_dists[n] = np.mean(oss)
    b = np.min(cluster_dists)
    # print(b)
    silhouettes[i] = (b - a)/np.maximum(b,a)
    # print(silhouettes[i])
  min_silhouette = 1.0
  for i in range(k):
    cluster_sil = np.mean(silhouettes[labels ==labels[i]])
    if cluster_sil < min_silhouette:
      min_silhouette = cluster_sil

  return min_silhouette

# a = np.array([0,1,2,3,4,5])
# b = np.array([0,0,1,1,2,2])
# avg_silhouette(a, b, 3)
# exit()

# define kernels to use for hit-or-miss filter
kernel_3 = np.ones((3, 3), np.uint8)
diamond = [[0, 0, 1, 0, 0],
           [0, 1, 1, 1, 0],
           [1, 1, 1, 1, 1],
           [0, 1, 1, 1, 0],
           [0, 0, 1, 0, 0]]
kernel_5_d = np.array(diamond, np.uint8)
kernel_5 = np.ones((5, 5), np.uint8)
kernel_7 = np.ones((7, 7), np.uint8)

# define character hit custom dtype
dtype = [('y', int), ('x', int), ('char', object)]

# iterate over all pages
for page_root, dirs, page_files in os.walk('2014onion7'):
  for page_file in page_files:
    if page_file[-4:] == '.jpg':
      num = page_file[:-4]
      print(page_file)
      # read and binarize page
      page = cv.imread(os.path.join(page_root, page_file), 0)
      ret, page = cv.threshold(page, 127, 255, cv.THRESH_BINARY)
      page = 255 - page

      # initialize variables
      # read_page = np.zeros_like(page, dtype='float64')
      all_chars = np.array([], dtype=dtype)

      # page_char = page/4

      # iterate over all characters
      for root, dirs, files in os.walk('cropped vocabulary'):
        for file in files:
          # extract character
          char, _ = file.split('.')
          # read and binarize character
          img = cv.imread(os.path.join(root, file), 0)
          ret, img = cv.threshold(img, 127, 255, cv.THRESH_BINARY)
          img = 255 - img
          
          # erode the character to make sure it matches on the page
          img_erode_1 = cv.erode(img, kernel_3)
          if char == '1_dot':
            # create a character outline for the hit or miss filter
            img_erode_2 = cv.dilate(img, kernel_5) - cv.dilate(img, kernel_3)
            filter_page = page
          elif char == 'D':
            # create a character outline for the hit or miss filter
            img_erode_2 = img - cv.erode(img, kernel_3)
            filter_page = cv.erode(page, kernel_5)
            filter_page = cv.erode(filter_page, kernel_5_d)
          else:
            # create a character outline for the hit or miss filter
            img_erode_2 = img - cv.erode(img, kernel_3)
            filter_page = cv.erode(page, kernel_7)
          # run hit or miss filter
          page_erode_1 = cv.erode(page, img_erode_1, borderValue=0)
          page_erode_2 = cv.erode(255 - filter_page, img_erode_2, borderValue=0)
          page_erode = np.logical_and(page_erode_1, page_erode_2)
          page_erode = page_erode.astype(np.uint8) * 255

          # check if character is present in image
          if sum(sum(page_erode)) > 0:

            # permute kernel to make image look correct
            kernel = np.fliplr(np.flipud(img))

            # create structured array with char and index groups
            char_indices = np.argwhere(page_erode)
            data = []
            for coords in char_indices.tolist():
              coords.append(char)
              data.append(tuple(coords))
            found_chars = np.array(data, dtype=dtype)

            # update character hit variables
            # read_page += cv.dilate(page_erode, kernel)/2
            all_chars = np.concatenate((all_chars, found_chars))

      # orig = os.path.join('docs', 'img', num + '_original.png')
      # hits = os.path.join('docs', 'img', num + '_hits.png')

      # read_page = read_page/np.max(np.max(read_page))
      # matplotlib.image.imsave(orig, np.repeat(page[:, :, np.newaxis], 3, axis=2))
      # matplotlib.image.imsave(hits, np.repeat(read_page[:, :, np.newaxis], 3, axis=2))

      # create char to index dict without repeats
      char2idx = {}
      for x, y, char in all_chars:
        if char in char2idx.keys():
          char2idx[char].append((x, y))
        else:
          char2idx[char] = [(x, y)]

      # create char to blob center dict
      char2centers = {}
      for char, indices in char2idx.items():
        while indices:
          x, y = indices[0]
          num_idx = len(indices)
          # call find_blob to identify the sum of blobx and y coords
          indices, x_sum, y_sum = find_blob(indices, x, y, 0, 0)
          blob_size = num_idx - len(indices)
          # average blob x and y coords to find center
          x = x_sum / blob_size
          y = y_sum / blob_size
          # add new blob center to blob center dict
          if char in char2centers.keys():
            char2centers[char].append((x, y))
          else:
            char2centers[char] = [(x, y)]

      # omit subcharacter hits
      char2centers = priotize_chars('13_dots', '1_dot', char2centers)
      char2centers = priotize_chars('4_dots', '1_dot', char2centers)
      char2centers = priotize_chars('Y', 'U', char2centers)
      char2centers = priotize_chars('R', 'W', char2centers)
      char2centers = priotize_chars('R', 'L', char2centers)

      # # create blank image
      # read_page = np.zeros_like(page, dtype='float64')

      # for key, values in char2centers.items():
      #   print(key)
      #   # read and binarize character
      #   img = cv.imread(os.path.join('cropped vocabulary', key + '.png'), 0)
      #   ret, img = cv.threshold(img, 127, 255, cv.THRESH_BINARY)
      #   img = 255 - img
      #   # flip kernel for display
      #   kernel = np.fliplr(np.flipud(img))
      #   # collect char locations
      #   char_page = np.zeros_like(page, dtype='float64')
      #   for value in values:
      #     char_page[int(value[0]),int(value[1])] = 255
      #   # erode chars onto blank image
      #   read_page += cv.dilate(char_page, kernel)/2

      # # normalize and display image
      # read_page = read_page/np.max(np.max(read_page))
      # hits = os.path.join('docs', 'img', num + '_prioritized.png')
      # matplotlib.image.imsave(hits, np.repeat(read_page[:, :, np.newaxis], 3, axis=2))

      # extract prioitized characters back into structured array
      data = []
      x_coords = []
      for key, values in char2centers.items():
        for x, y in values:
          data.append((x, y, key))
          x_coords.append((x)) 

      points = np.array(x_coords)
      points = np.sort(points)
      print(points)

      max_k = 15
      best_silhouette = -1.0
      for k in range(1, max_k):
        silhouette = 1.0
        while silhouette == 1.0:
          centroids, labels = k_means(points, k + 1)
          silhouette = avg_silhouette(points, labels, k + 1)
          print(k, silhouette)
        if silhouette > best_silhouette:
          best_silhouette = silhouette
          best_centroids = centroids
          best_labels = labels
      print(best_centroids)
      print(best_labels)
      exit()

      # order characters top to bottom, left to right
      ordered_chars = np.array(data, dtype=dtype) 
      transcript = np.sort(ordered_chars, order=['y', 'x'])
      
      if transcript.shape[0] > 0:
        # identify upper and lower bounds of character centroids
        min_y = transcript[0][0]
        max_y = transcript[-1][0]

        # approximate number of lines and their y positions
        num_lines = np.ceil((max_y - min_y)/200) + 1

        bins = np.linspace(min_y, max_y, num_lines)

        bin_num = 0
        for idx, letter in enumerate(transcript):
          y, x, char = letter
          # if no more characters are in the current bin, move on
          while y < bins[bin_num] - 100 or  y > bins[bin_num] + 100:
            bin_num += 1
          # set character y value to bin value
          transcript[idx] = (bins[bin_num], x, char)

        # resort the transcript with new y values
        idx_transcript = np.sort(transcript, order=['y', 'x'])

        # replace dots with punctuation
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

      else:
        transcript = []

      # check for transcript folder
      if not(os.path.exists('transcripts')):
        os.makedirs('transcripts')

      # write out transcript
      filepath = os.path.join('transcripts', page_file[:-4] + '.json')
      with open(filepath, 'w') as f:
        json.dump(transcript, f)
