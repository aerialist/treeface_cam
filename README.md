# treeface_cam
Detect face from camera and put onto a picture. You can use it as a fake camera for web conference by combining it with a tool like CamTwist.

I want to be a wise old man in the tree...

After running manay web conferences from home, I wanted a camera that can only show my face; hiding all the background.
Fake background feature in Zoom is great but my PC is not powerful enough and requires green screen which still hard for me to prepare.

Fortunetely face detection by OpenCV seems to run fast and not require too much power.

# To run

You would need quite a few things to run the code.
I'd recommend to use Anaconda and setup an environment with following:

* Python3
* opencv
* pillow
* numpy
* PyQt5

# To use it as a web camera

To use it as a web camera for web conference applications, you would need a software tool as grab a window and output as a web camera.

On MacOS, one such tool is CamTwist.

# Thank you
Face detection by haarcascade face classifier

* https://github.com/opencv/opencv/tree/master/data/haarcascades
* https://docs.opencv.org/3.4/db/d28/tutorial_cascade_classifier.html

This blog post by Otulagun Daniel Oluwatosin shows how to do most of the things.

Facial Landmarks and Face Detection in Python with OpenCV

https://medium.com/analytics-vidhya/facial-landmarks-and-face-detection-in-python-with-opencv-73979391f30e

# Attribution

37324474485_2bb351135a_c.jpg
CC BY 2.0 by NakaoSodanshitsu 
https://www.flickr.com/photos/nakaosodanshitsu/37324474485/in/dateposted-public/

247929876_624.v1588294834.jpg
CC BY 2.0 by Hide
http://photozou.jp/photo/show/2994695/247929876

wood-tree-spruce-picea.jpg
CC0
https://www.piqsels.com/en/public-domain-photo-smgls

the-big-tree-on-the-bank.jpg
CC0
https://www.publicdomainpictures.net/cn/view-image.php?image=23597&picture=

big-tree-200-years-old-ancient-wallpaper-preview.jpg
CC0
https://www.peakpx.com/604794/brown-tree-trunk

1ca8dd493729a9f4dcd9a33f52fb-1585965.jpg
CC0
https://pxhere.com/ja/photo/1585965