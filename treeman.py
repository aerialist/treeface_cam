"""

To debug code in Qt event loop, call pyqtRemoveInputHook before set_trace
pyqtRemoveInputHook()
import pdb; pdb.set_trace()

"""

import sys
import time
import threading
import argparse

import cv2
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QLabel, QDialog, QFileDialog
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QCheckBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, pyqtRemoveInputHook

RESOLUTION_WIDTH = 640
RESOLUTION_HEIGHT = 360
RES = (RESOLUTION_WIDTH, RESOLUTION_HEIGHT)
MAGIC_NUMBER = 14 # Upper left corner of QLabel position

def pil2cv(image):
    ''' 
    PIL型 -> OpenCV型 
    https://qiita.com/derodero24/items/f22c22b22451609908ee
    '''
    new_image = np.array(image, dtype=np.uint8)
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)
    return new_image

def cv2pil(image):
    ''' 
    OpenCV型 -> PIL型 
    https://qiita.com/derodero24/items/f22c22b22451609908ee
    '''
    new_image = image.copy()
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGRA2RGBA)
    new_image = Image.fromarray(new_image)
    return new_image

class ClickLabel(QLabel):
    """
    Overload mousePressEvent of QLabel to send position of mouse click
    """
    label_clicked = pyqtSignal(QPoint, name="labelClicked")

    def mousePressEvent(self, event):
        #print(event.pos())
        self.label_clicked.emit(event.pos())

class TreeMan(QMainWindow):
    """
    """
    def __init__(self, cam=0):
        QMainWindow.__init__(self)
        self.setupUi()

        self.cam = cam
        self.bg = self.load_bg()
        self.running = True
        self.multiplier = 1.0
        self.target_center = (int(RESOLUTION_WIDTH/2), int(RESOLUTION_HEIGHT/2))

        self.btn_bg.clicked.connect(self.on_btn_bg_clicked)
        self.btn_pause.clicked.connect(self.on_btn_pause_clicked)
        self.btn_wider.clicked.connect(self.on_btn_bigger_clicked)
        self.btn_narrower.clicked.connect(self.on_btn_smaller_clicked)
        self.ck_mode.stateChanged.connect(self.on_ch_mode_stateChanged)
        self.label_qpixmap.label_clicked.connect(self.on_image_clicked)

        self.thread_update_image = threading.Thread(target=self.update_image, daemon=True)
        self.thread_update_image.start()
    
    def setupUi(self):
        self.setWindowTitle("Treeman")
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        #self.label_qpixmap = QLabel("Hello World!!")
        self.label_qpixmap = ClickLabel("Hello World!!")
        self.label_qpixmap.setFixedSize(RESOLUTION_WIDTH, RESOLUTION_HEIGHT)
        self.btn_pause = QPushButton("Pause")
        self.btn_bg = QPushButton("Background")
        self.ck_mode = QCheckBox("Fix location")
        self.btn_narrower = QPushButton("Narrower")
        self.btn_wider = QPushButton("Wider")
        self.layoutH = QHBoxLayout()
        self.layoutH.addWidget(self.btn_bg)
        self.layoutH.addWidget(self.btn_pause)
        self.layoutH.addWidget(self.ck_mode)
        self.layoutH.addWidget(self.btn_wider)
        self.layoutH.addWidget(self.btn_narrower)

        self.layout.addWidget(self.label_qpixmap)
        self.layout.addLayout(self.layoutH)
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

    def update_image(self):
        """
        """
        cap = cv2.VideoCapture(self.cam)
        time.sleep(1)
        # these resolution setting doesn't seem to work...
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, RESOLUTION_WIDTH) # width resolution
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT,RESOLUTION_HEIGHT) # height resolution
        #camera_fps_counter = 0
        haarcascade = "haarcascade_frontalface_alt2.xml"
        detector = cv2.CascadeClassifier(haarcascade)
        while True:
            if self.running == False:
                time.sleep(0.5)
                continue
            _, frame = cap.read()
            frame = cv2.resize(frame, RES)
            #current_counter = time.perf_counter()
            #camera_interval = current_counter - camera_fps_counter
            #camera_fps_counter = current_counter
            #self.ui.label_fps.setText("{:.3f}s {}FPS".format(camera_interval, int(1/camera_interval)))
            #print("{:.3f}s {}FPS".format(camera_interval, int(1/camera_interval)))
            #print(frame.shape)

            # detect face
            image_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(image_gray)
            #print("Faces:\n", faces)
            # for face in faces:
            #     #     save the coordinates in x, y, w, d variables
            #     (x,y,w,d) = face
            #     # Draw a white coloured rectangle around each face using the face's coordinates
            #     # on the "image_template" with the thickness of 2 
            #     cv2.rectangle(frame,(x,y),(x+w, y+d),(255, 255, 255), 2)

            img = cv2pil(frame)
            if len(faces) == 0:
                # No face found. 
                continue
            face = faces[0] # TODO: handle multiple detection
            if len(face) == 4:
                if face[2]<40:
                    # too small. Most likely false detection
                    continue
                if self.multiplier != 1.0:
                    face = self.resize_face(face)
                if self.ck_mode.isChecked():
                    # fixed location mode
                    mask = Image.new('L', (face[2], face[3]), 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse([(20,20), (face[2]-20, face[3]-20)], fill=255, outline=None, width=10)
                    del(draw)
                    mask = mask.filter(ImageFilter.GaussianBlur(10)) # adjust radius according to face area size
                    box = (face[0], face[1], face[0]+face[2], face[1]+face[3])
                    img_crop = img.crop(box)
                    embed_box = (self.target_center[0]-int(face[2]/2),
                                 self.target_center[1]-int(face[3]/2),
                                 self.target_center[0]-int(face[2]/2) + face[2], 
                                 self.target_center[1]-int(face[3]/2) + face[3])
                    img = self.bg.copy()
                    img.paste(img_crop, box=embed_box, mask=mask)

                else:
                    mask = Image.new('L', RES, 255)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse([(face[0], face[1]), (face[0]+face[2], face[1]+face[3])], fill=0, outline=None, width=10)
                    del(draw)
                    mask = mask.filter(ImageFilter.GaussianBlur(20)) # adjust radius according to face area size
                    img = Image.composite(self.bg, img, mask)
            else:
                continue

            # draw image as QPixmap on QLabel
            label_width = self.label_qpixmap.width()
            label_height = self.label_qpixmap.height()
            self.label_qpixmap.setPixmap(img.toqpixmap().scaled(
                label_width, label_height,
                Qt.KeepAspectRatio, Qt.SmoothTransformation))

        cap.release()
        #cv2.destroyAllWindows()

    def resize_img(self, img1, img2):
        """
        Resize img2 to similar size as img1
        """
        size1 = img1.size
        size2 = img2.size
        ratio_x = size1[0]/size2[0]
        ratio_y = size1[1]/size2[1]
        if ratio_x > ratio_y:
            ratio = ratio_y
        else:
            ratio = ratio_x
        new_size_x = int(size2[0]*ratio)
        new_size_y = int(size2[1]*ratio)
        new_size = (new_size_x, new_size_y)
        return img2.resize(new_size)

    def resize_face(self, face):
        """
        Modify detected face area by self.multiplier, keeping the center position
        """
        (x,y,w,d) = face
        new_w = int(w * self.multiplier)
        new_d = int(d * self.multiplier)
        new_x = int((x+w/2) - new_w/2)
        new_y = int((y+d/2) - new_d/2)
        return (new_x,new_y,new_w,new_d)

    def find_center_upperleft_corner(self, im1, im2):
        """
        Return im2's upper left corner cordinate when im1 and im2 are overlayed with their centers aligned
        Assuming size of im2 is smaller than im1
        """
        x1, y1 = im1.size
        x2,y2 = im2.size
        center_x1 = int(x1/2)
        center_y1 = int(y1/2)
        center_x2 = int(x2/2)
        center_y2 = int(y2/2)
        x = center_x1 - center_x2
        y = center_y1 - center_y2
        return (x, y)

    def load_bg(self, fname_bg="sakura.jpg"):
        """
        Load background image
        select a file, resize it to fit in RES size with black background
        """
        img_bg = Image.open(fname_bg)
        bg_black = Image.new('RGB', RES, (0,0,0))
        img_bg_resize = self.resize_img(bg_black, img_bg)
        target_box = self.find_center_upperleft_corner(bg_black, img_bg_resize)
        bg_black.paste(img_bg_resize, box=target_box)
        return bg_black

    def on_btn_bg_clicked(self):
        filename, _ = QFileDialog.getOpenFileName(self, 
                        "Choose a background picture",
                        "",
                        "Images (*.png *.jpg *jpeg *gif *bmp)")
        if filename:
            self.bg = self.load_bg(filename)

    def on_btn_pause_clicked(self):
        if self.running:
            self.btn_pause.setText("Run")
            self.running = False
        else:
            self.btn_pause.setText("Pause")
            self.running = True

    def on_btn_bigger_clicked(self):
        self.multiplier += 0.1

    def on_btn_smaller_clicked(self):
        self.multiplier -= 0.1

    def on_image_clicked(self, pos):
        self.target_center = (pos.x(), pos.y())
    
    def on_ch_mode_stateChanged(self, state):
        """
        Adjust area size due difference by mask size
        """
        adjustment = 0.3
        if state == Qt.Checked:
            self.multiplier += adjustment
        else:
            self.multiplier -= adjustment

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Treeman')
    parser.add_argument('-c', '--camera_id', type=int, default=0,
                        help='Camera ID: default 0.',)
    args = parser.parse_args()

    app = QApplication(sys.argv)
    win = TreeMan(args.camera_id)
    win.show()
    sys.exit(app.exec_())
