# voronoi-diagram
## please See the ppt
Voronoi Art

Lin Wang 

We choose Voronoi art for our project. For a given image and the number of points, our program can generate a Voronoi painting according to the original image. The flow chart is shown in Figure 1.
 
Figure 1. Program flow chart
![image](https://github.com/1e0n-xx/voronoi-diagram/blob/master/Voronoi%20diagram/figure%20(2).jpg)
Figure 2 shows a picture of the Rotunda, and we take this image as an example to explain how we achieve the work.
 ![image](https://github.com/1e0n-xx/voronoi-diagram/blob/master/Voronoi%20diagram/figure%20(3).jpg)
Figure 2. Example image

First, we read the origin image into the program as a matrix, and blur it for a better performance. Then, we use canny edge detection to find the edges on the image. After that, we dilate the edge, and make subtraction of the two images. The aim of this step is to avoid putting points on the edge, or somewhere with little color difference. The process is shown through Figure 3 to 5.
 
Figure 3. Edge detection
 
Figure 4. Edge dilation
 
Figure 5. Subtraction
Next, we randomly generate points on the image. Notice that we put points in the white area in Figure 5 with a high probability. If a point is chosen, we also set its neighbor points as chosen, to avoid choosing point too close.
After that, we connect these points with Delaunay triangulation, and obtain the Voronoi diagram in this process. The Delaunay triangulation and the Voronoi diagram are shown in Figure 6 and Figure 7.
 
Figure 6. Delaunay triangulation
 
Figure 7. Voronoi diagram
Finally, we paint the Voronoi diagram with the original image. We divide the Voronoi diagram into small pieces, and flood fill each piece with the mean color of that region in the original image. However, the picture still has white edge on it. To get rid of it, we blur the image, and fill the white edge with the color on the blurred version. The process is shown through Figure 8 to 10.
 
Figure 8. mean & flood fill
 
Figure 9. Blur
 
Figure 10. Final result

