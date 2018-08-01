# Getting Our Characters in a Row

Alright, so we have a list of true positive centroid-character pairs, but we're still an unorganized mess! Having the characters doesn't do us much good if we can't get the words. We need a way to organize the characters according to line, and then by their position in the line. The naive method would be to organize the centroids by y coordinate, and then by x coordinate. This method results in a jumbled mess due to minute variance in the character centroids. We need to find a more robust way of separating characters into their lines, from which point sorting by x coordinate should result in a correct transcription.

### k-means Clustering

k-means is an extremely simple and effective way of separating data into *k* clusters. k-means would be fantastic if we had a fixed number of lines in all the images, which we don't.

 Page 0 | Page 57
:------:|:-------:
![page 0](https://raw.githubusercontent.com/ralphatobe/cicada-3301/master/docs/img/0_original.png "Page 0") | ![page 57](https://raw.githubusercontent.com/ralphatobe/cicada-3301/master/docs/img/57_original.png "Page 57")
