
|  Y  |  X  | Character |
|:---:|:---:|:---------:|
 729|  656| AE 
 729|  783| H 
 :|  :| :
 729| 1592| Y
 730|  617| R 
 :| :| :
 730| 1782| 1_dot
 731| 1014| F
 731| 1186| D




# Getting Our Characters in a Row

Alright, so we have a list of true positive centroid-character pairs, but we're still an unorganized mess! Having the characters doesn't do us much good if we can't get the words. We need a way to organize the characters according to line, and then by their position in the line. The naive method would be to organize the centroids by y coordinate, and then by x coordinate. This method results in a jumbled mess due to minute variance in the character centroids. We need to find a more robust way of separating characters into their lines, from which point sorting by x coordinate should result in a correct transcription.

### k-means Clustering

k-means is an extremely simple and effective way of separating data into *k* clusters. k-means would be fantastic if we had a fixed number of lines in all the images, which we don't. The images don't even have consistent spacing between lines!

 Page 0 | Page 57
:------:|:-------:
![page 0](https://raw.githubusercontent.com/ralphatobe/cicada-3301/master/docs/img/0_original.png "Page 0") | ![page 57](https://raw.githubusercontent.com/ralphatobe/cicada-3301/master/docs/img/57_original.png "Page 57")

So not only do we need a way to separate y coordinates into lines, but we also need to identify the number of lines in the image. Luckily, we just happen to have an algorithm for this task. Introducing...

### Silhouette

Silhouette is a method that can be maximized to tentatively identify the correct number of clusters for a set of points. Silhouette is a measure computed for each point in a dataset that has already been clustered by some algorithm. For each point *i*, let *a(i)* be the average distance between *i* and each other point in *i*'s cluster. *a(i)* functionally measures how well *i* fits in its cluster. This function can be formalized by defining *S(i)*, which returns all other points in *i*'s cluster. We can now define *a(i)*:

Likewise let *b(i)* be the lowest average distance from *i* to all points in another cluser. *b(i)* is a measure of how overfit the data is; *b(i)* gives us a measure of how dense the clusters are by returning the average distance to *i*'s "neighboring cluster". Using these two values, silhouette is defined as

<a href="https://www.codecogs.com/eqnedit.php?latex=s(i)=\frac{b(i)-a(i)}{\mathbf{max}\left&space;\{&space;a(i),b(i)&space;\right&space;\}}" target="_blank"><img src="https://latex.codecogs.com/gif.latex?s(i)=\frac{b(i)-a(i)}{\mathbf{max}\left&space;\{&space;a(i),b(i)&space;\right&space;\}}" title="s(i)=\frac{b(i)-a(i)}{\mathbf{max}\left \{ a(i),b(i) \right \}}" /></a>

This equation can be reformulated as

<a href="https://www.codecogs.com/eqnedit.php?latex=\left\{\begin{matrix}&space;1-a(i)/b(i),&space;&&space;\textup{if}\;&space;a(i)<b(i)\\&space;0,&space;&&space;\textup{if}\;&space;a(i)=b(i)\\&space;a(i)/b(i)-1,&space;&&space;\textup{if}\;&space;a(i)>b(i)&space;\end{matrix}\right." target="_blank"><img src="https://latex.codecogs.com/gif.latex?\left\{\begin{matrix}&space;1-a(i)/b(i),&space;&&space;\textup{if}\;&space;a(i)<b(i)\\&space;0,&space;&&space;\textup{if}\;&space;a(i)=b(i)\\&space;a(i)/b(i)-1,&space;&&space;\textup{if}\;&space;a(i)>b(i)&space;\end{matrix}\right." title="\left\{\begin{matrix} 1-a(i)/b(i), & \textup{if}\; a(i)<b(i)\\ 0, & \textup{if}\; a(i)=b(i)\\ a(i)/b(i)-1, & \textup{if}\; a(i)>b(i) \end{matrix}\right." /></a>

It's clear from our reformulation that

<a href="https://www.codecogs.com/eqnedit.php?latex=-1\leq&space;s(i)\leq&space;1" target="_blank"><img src="https://latex.codecogs.com/gif.latex?-1\leq&space;s(i)\leq&space;1" title="-1\leq s(i)\leq 1" /></a>

This means that *s(i)* is maximized when *a(i)* is much less than *b(i)*. *a(i)* is minimized when a point is well-suited to its cluster and the cluster itself is adequately dense. *b(i)* is maximized when a point is ill-suited to its "neighboring cluster". We should see a significant dropoff in silhouette when the actual number of clusters (lines) in our data is exceeded because of how tightly clustered the y coordinates are in each line.

