import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


import os
import copy
import numpy as np
from PIL import Image
import math
from datetime import datetime
from PIL import Image
import cv2
import h5py
import qimage2ndarray
import time
from videoConverterTest import convertVideo

DEFAULTDISPLAYERWIDTHRANGE = 10000
DEFAULTDISPLAYERHEIGHTRANGE = 10000
DEFAULTFRAMERATERANGE = 120

DEFAULTMAXIMUMPATTERNLENGTHRANGE = 10000
DEFAULTMAXIMUMPATTERNLENGTH = 2000
DEFAULTSTARTTIMINGOFTHEMOVEMENT = 1000
DEFAULTENDTIMINGOFTHEMOVEMENT = 1500

DEFAULTDISPLAYERWIDTH = 360
DEFAULTDISPLAYERHEIGHT = 720
DEFAULTFRAMERATE = 120

DEFAULTBARWIDTH = 35
DEFAULTINITIALBARMIDPOINTPOSITION = 360
DEFAULTFINALBARMIDPOINTPOSITION = 540

DEFAULTSPOTWIDTH = 35 
DEFAULTSPOTHEIGHT = 35
DEFAULTINITIALSPOTMIDPOINTXPOSITION = 360
DEFAULTFINALSPOTMIDPOINTXPOSITION = 540
DEFAULTINITIALSPOTMIDPOINTYPOSITION = 180
DEFAULTFINALSPOTMIDPOINTYPOSITION = 180

DEFAULTDISPLAYCOVERINGANGLE = 328
DEFAULTINITIALLOOMINGMIDPOINTXPOSITION = 360
DEFAULTINITIALLOOMINGMIDPOINTYPOSITION = 180
DEFAULTINITIALDISCRADIUS = 7.5
DEFAULTFINALDISCRADIUS = 120

DEFAULTGRATINGCYCLELENGTH = 70
DEFAULTGRATINGLOCATIONDIFFERENCE = 49

class savingChangedImageIndexThread(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
    
    def run(self):
        self.parent.label1.setPixmap(patternGenerator.QPixmapArray[self.parent.slider.value()])
        self.parent.updateCurrentIndexText()
        
class convertVideoThread(QThread):
    update_progress = pyqtSignal(int)
    def __init__(self, input_path, output_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.input_path = input_path
        self.output_path = output_path
        
        self._is_running = True
    def run(self):
        convertVideo(self.input_path, self.output_path, self.update_progress, self)
        
    def stop(self):
        self._is_running = False

class playingImageThread(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
    
    def run(self):
        self.parent.playFlag = True
        initialTime = QTime.currentTime()
        #print("initialTime")
        #print(initialTime)
        initialFrameIndex = self.parent.slider.value()
        frameRate = patternGenerator.currentvideoFrameRate 

        fdtemp = 0

        while((self.parent.slider.value() != len(patternGenerator.QPixmapArray)-1) and (self.parent.playFlag == True)):
            currentTime = QTime.currentTime()
            timeDifference = initialTime.msecsTo(currentTime)
            frameDifference = int(timeDifference * frameRate // 1000)

            if(frameDifference != fdtemp):
                self.parent.slider.setValue(initialFrameIndex + frameDifference)
                #print(currentTime, timeDifference, frameDifference, self.parent.slider.value())

            fdtemp = frameDifference

class resettingFlagThread(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
    
    def run(self):
        self.parent.playFlag = False

class generatedPatternWindow(QDialog,QIcon):

    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        layout = QHBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        mainlayout = QVBoxLayout()

        self.label1 = QLabel()
        self.displayImage = QPixmap()

        self.pushbutton1 = QPushButton()
        self.pushbutton2 = QPushButton()
        self.pushbutton3 = QPushButton()
        self.pushbutton4 = QPushButton()

        self.pushbutton1.setFixedSize(30,30)
        self.pushbutton2.setFixedSize(30,30)
        self.pushbutton3.setFixedSize(30,30)
        self.pushbutton4.setFixedSize(30,30)

        self.pushbutton1.setIcon(QIcon('blue255.jpg'))
        self.pushbutton2.setIcon(QIcon('white255.jpg'))
        self.pushbutton3.setIcon(QIcon('test.jpg'))
        self.pushbutton4.setIcon(QIcon('random_frame.jpg'))

        self.pushbutton1.setIconSize(QSize(30,30))
        self.pushbutton2.setIconSize(QSize(30,30))
        self.pushbutton3.setIconSize(QSize(30,30))
        self.pushbutton4.setIconSize(QSize(30,30))

        self.pushbutton1.setFocusPolicy(Qt.NoFocus)
        self.pushbutton2.setFocusPolicy(Qt.NoFocus)
        self.pushbutton3.setFocusPolicy(Qt.NoFocus)
        self.pushbutton4.setFocusPolicy(Qt.NoFocus)

        self.btnGroup = QButtonGroup()
        self.btnGroup.setExclusive(False)
        self.btnGroup.addButton(self.pushbutton1)
        self.btnGroup.addButton(self.pushbutton2)
        self.btnGroup.addButton(self.pushbutton3)
        self.btnGroup.addButton(self.pushbutton4)

        self.playFlag = False

        self.pushbutton1.pressed.connect(lambda : self.goToPreviousImage())
        self.pushbutton2.pressed.connect(lambda : self.playImageThread())
        self.pushbutton3.pressed.connect(lambda : self.resetFlag())
        self.pushbutton4.pressed.connect(lambda : self.goToNextImage())

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, len(patternGenerator.QPixmapArray)-1)
        self.slider.setValue(0)
        self.slider.setPageStep(1)
        self.slider.setFixedSize(300,30)

        self.label2 = QLabel()

        self.updateCurrentIndexText()

        self.slider.valueChanged.connect (lambda : self.saveChangedImageIndexThread())

        #print(len(patternGenerator.QPixmapArray))
        self.label1.setPixmap(patternGenerator.QPixmapArray[0])

        layout.addStretch(1)
        layout.addWidget(self.label1)
        layout.addStretch(1)

        layout2.addStretch(1)
        layout2.addWidget(self.pushbutton1)
        layout2.addWidget(self.pushbutton2)
        layout2.addWidget(self.pushbutton3)
        layout2.addWidget(self.pushbutton4)
        layout2.addStretch(1)

        layout3.addStretch(5)
        layout3.addWidget(self.slider)
        layout3.addWidget(self.label2)

        layout3.addStretch(5)

        mainlayout.addLayout(layout)
        mainlayout.addLayout(layout2)
        mainlayout.addLayout(layout3)

        self.setWindowTitle('Generated Pattern')
        self.setLayout(mainlayout)
        self.setWindowModality(Qt.ApplicationModal)

    def saveChangedImageIndexThread(self):
        saveChangedImageIndexThread = savingChangedImageIndexThread(self)
        saveChangedImageIndexThread.start()

    def playImageThread(self):
        playImageThread = playingImageThread(self)
        playImageThread.start()

    def resetFlag(self):
        resetFlagThread = resettingFlagThread(self)
        resetFlagThread.start()

    #need to change string style
    def updateCurrentIndexText(self):
        self.currentIndexText = str(self.slider.value()) + "/" + str(len(patternGenerator.QPixmapArray)-1)
        self.label2.setText(self.currentIndexText)

    def goToPreviousImage(self):
        self.slider.setValue(self.slider.value()-1)
        #print(self.slider.value())

    def goToNextImage(self):
        self.slider.setValue(self.slider.value()+1)
        #print(self.slider.value())
    
class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        
        self.mainLayout = QVBoxLayout()
        self.generatorLayout = QVBoxLayout()
        self.generator_type_tab = QTabWidget()
        
        stylesheet = """ 
            QTabWidget>QWidget>QWidget{background: rgb(240,240,240);}
            """
        self.generator_type_tab.setStyleSheet(stylesheet)


        #videoTab = self.createVideoTab()
        patternTab = self.createPatternTab()
        videoTab = self.createVideoTab()
        

        self.currentActivatedGeneratorTabIndex = 0
        self.generator_type_tab.currentChanged.connect(lambda : self.saveActivatedGeneratorTab())
        self.generator_type_tab.addTab(patternTab, "Pattern")
        self.generator_type_tab.addTab(videoTab, "Video")

        self.generatorLayout.addWidget(self.generator_type_tab)

        


        #alginment of layouts
        

        #self.setLayout(self.mainLayout)
        self.mainLayout.addLayout(self.generatorLayout)
        self.setLayout(self.mainLayout)

        #set window format
        self.setWindowIcon(QIcon('blue255.jpg'))
        self.setWindowTitle('Pattern Generator')
        self.move(300, 300)
        #self.setFixedSize(500,600)
        self.resize(700, 700) # set window size
        self.show()

    ### 수정사항1
    def saveGeneratedPatternasHDF(self):
        if(self.isPatternGenerated == False): return

        FileSave = QFileDialog.getSaveFileName(self, 'Save file', "","h5 file (*.h5 *.hdf)")    # <- Here
        #f = h5py.File(FileSave[0]+".hdf5", "w")

        # End if push cancle button or take empty file name
        if FileSave[0] == "":
            return
        f = h5py.File(FileSave[0], "w")

        if(self.generatedPatternindex == 0): #bar
            f.create_dataset("imagedset", data = self.barImagedset)
            f.create_dataset("timesequenceNpositiondset", data = self.TimeSequenceNBarLocationdset)
            f.create_dataset("totalpatternlength", data = self.currenttotalPatternLength)
        elif(self.generatedPatternindex == 1): #spot
            f.create_dataset("imagedset", data = self.spotImagedset)
            f.create_dataset("timesequenceNpositiondset", data = self.TimeSequenceNSpotLocationdset)
            f.create_dataset("totalpatternlength", data = self.currenttotalPatternLength)
        elif(self.generatedPatternindex == 2): #looming
            f.create_dataset("imagedset", data = self.loomingImagedset)
            f.create_dataset("timesequenceNpositiondset", data = self.TimeSequenceNDiscLocationdset)
            f.create_dataset("totalpatternlength", data = self.currenttotalPatternLength)
        elif(self.generatedPatternindex == 3): #grating
            f.create_dataset("imagedset", data = self.gratingImagedset)
            f.create_dataset("timesequenceNpositiondset", data = self.TimeSequenceNGratingLocationdset)
            f.create_dataset("totalpatternlength", data = self.currenttotalPatternLength)

        f.close
        ## test
    def saveGeneratedPatternasSequentialImage(self):
        if(self.isPatternGenerated == False): return
        
        FileSave = QFileDialog.getSaveFileName(self, 'Save file', "","mp4 file (*.mp4)")
        # End if push cancle button or take empty file name
        # FileSave[0] == FileName
        if FileSave[0] == "": return

        if(self.generatedPatternindex == 0): #bar
            mp4imageset = copy.deepcopy(self.barImageArray)
        elif(self.generatedPatternindex == 1): #spot
            mp4imageset = copy.deepcopy(self.spotImageArray)
        elif(self.generatedPatternindex == 2): #looming
            mp4imageset = copy.deepcopy(self.loomingImageArray)
        elif(self.generatedPatternindex == 3): #grating
            mp4imageset = copy.deepcopy(self.gratingImageArray)
                
        width,height = mp4imageset[0].size


        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can change the codec as needed
        output_video = cv2.VideoWriter(FileSave[0], fourcc, self.video_frame_rate_value[0], (width, height))

        for i in range(len(mp4imageset)):
            temp = np.array(mp4imageset[i])
            temp = cv2.cvtColor(temp, cv2.COLOR_RGB2BGR)
            output_video.write(temp)

        output_video.release()


    def saveGeneratedPatternasGIF(self):
        if(self.isPatternGenerated == False): return

        FileSave = QFileDialog.getSaveFileName(self, 'Save file', "","gif file (*.gif)")
        # End if push cancle button or take empty file name
        # FileSave[0] == FileName
        if FileSave[0] == "":
            return
        
        if(self.generatedPatternindex == 0): #bar
            gifimageset = copy.deepcopy(self.barImageArray)
        elif(self.generatedPatternindex == 1): #spot
            gifimageset = copy.deepcopy(self.spotImageArray)
        elif(self.generatedPatternindex == 2): #looming
            gifimageset = copy.deepcopy(self.loomingImageArray)
        elif(self.generatedPatternindex == 3): #grating
            gifimageset = copy.deepcopy(self.gratingImageArray)
                
        dir  = FileSave[0]
        gifimageset[0].save(dir, save_all=True, append_images=gifimageset[1:], optimize = False, duration = 20, loop=0)


    def showGeneratedPattern(self):
        if(self.isPatternGenerated == False): return

        self.ex = generatedPatternWindow()
        self.ex.show()

    def generatePattern(self):
        if self.video_frame_rate_value[0] > 50:
            self.save_generated_pattern_as_gif_push_button.setDisabled(True)
        else:
            self.save_generated_pattern_as_gif_push_button.setEnabled(True)


        if(self.currentActivatedTabIndex == 0): self.generateBarPattern()
        if(self.currentActivatedTabIndex == 1): self.generateSpotPattern() 
        if(self.currentActivatedTabIndex == 2): self.generateLoomingPattern()
        if(self.currentActivatedTabIndex == 3): self.generateGratingPattern()

    def generateBarPattern(self):
        if(self.currentBarCnt[0] == 0): return

        self.isPatternGenerated = True
        self.generatedPatternindex = 0

        currentDisplayHeight = self.displayer_height_value[0]
        currentDisplayWidth = self.displayer_width_value[0]
        self.currenttotalPatternLength = self.bar_total_pattern_duration_spin_box_value[0]
        self.currentvideoFrameRate = self.video_frame_rate_value[0]
        ncurrentTotalFrame =   math.trunc(self.currenttotalPatternLength / 1000 * self.currentvideoFrameRate)
        currentTotalBarPatternInformation= self.totalBarInformation
        backgroundColorBGR = self.bar_background_color

        self.TimeSequenceNBarLocationdset = np.zeros((ncurrentTotalFrame,1+len(currentTotalBarPatternInformation)),np.float32)
        self.barImagedset = np.zeros((ncurrentTotalFrame,currentDisplayHeight,currentDisplayWidth,3), np.uint8)

        img = np.zeros((currentDisplayHeight,currentDisplayWidth,3), np.uint8)
        img[:,:,:] = backgroundColorBGR

        self.CheckOverTotalDuration(self.currenttotalPatternLength, currentTotalBarPatternInformation, 8)

        for i in range(ncurrentTotalFrame):
            self.TimeSequenceNBarLocationdset[i][0] = ('{:.3f}'.format(i / self.currentvideoFrameRate * 1000))
            self.barImagedset[i] = img.copy()

        for i in range(len(currentTotalBarPatternInformation)):

            if(currentTotalBarPatternInformation[i][4] == currentTotalBarPatternInformation[i][5]):
                for j in range(ncurrentTotalFrame):
                    self.TimeSequenceNBarLocationdset[j,i+1] = currentTotalBarPatternInformation[i][4]
            elif(currentTotalBarPatternInformation[i][6] == "sigmoid"):
                for j in range(ncurrentTotalFrame):
                    self.TimeSequenceNBarLocationdset[j,i+1] = self.sigmoidFunc(self.TimeSequenceNBarLocationdset[j][0], 
                                                                                currentTotalBarPatternInformation[i][4], 
                                                                                currentTotalBarPatternInformation[i][5], 
                                                                                currentTotalBarPatternInformation[i][7], 
                                                                                currentTotalBarPatternInformation[i][8])
            else:
                for j in range(ncurrentTotalFrame):
                    self.TimeSequenceNBarLocationdset[j,i+1] = self.linearFunc(self.TimeSequenceNBarLocationdset[j][0], 
                                                                               currentTotalBarPatternInformation[i][4], 
                                                                               currentTotalBarPatternInformation[i][5], 
                                                                               currentTotalBarPatternInformation[i][7], 
                                                                               currentTotalBarPatternInformation[i][8])

        for i in range(len(currentTotalBarPatternInformation)):
            barColorBGR = currentTotalBarPatternInformation[i][1]
            barWidth = currentTotalBarPatternInformation[i][2]
            barHalfWidth = barWidth // 2

            if(currentTotalBarPatternInformation[i][3] == "vertical"):
                for j in range(ncurrentTotalFrame):
                    self.barImagedset[j] = cv2.rectangle(self.barImagedset[j],
                                                         (0,int(self.TimeSequenceNBarLocationdset[j][i+1])-barHalfWidth-1),
                                                         (currentDisplayWidth-1,int(self.TimeSequenceNBarLocationdset[j][i+1])+barHalfWidth-1),
                                                         barColorBGR,-1)
            else:
                for j in range(ncurrentTotalFrame):
                    self.barImagedset[j] = cv2.rectangle(self.barImagedset[j],
                                                         (int(self.TimeSequenceNBarLocationdset[j][i+1])-barHalfWidth-1,0),
                                                         (int(self.TimeSequenceNBarLocationdset[j][i+1])+barHalfWidth-1,currentDisplayHeight-1),
                                                         barColorBGR,-1)
                
        self.barImageArray = []
        self.barQImageArray = []
        self.QPixmapArray = []

        for i in range(ncurrentTotalFrame):
            self.barImageArray.append(Image.fromarray(self.barImagedset[i]))
            self.barQImageArray.append(qimage2ndarray.array2qimage(self.barImagedset[i], normalize=False))
            self.QPixmapArray.append(QPixmap.fromImage(self.barQImageArray[i]))




    def generateSpotPattern(self):
        if(self.currentSpotCnt[0] == 0): return

        self.isPatternGenerated = True
        self.generatedPatternindex = 1

        currentDisplayHeight = self.displayer_height_value[0]
        currentDisplayWidth = self.displayer_width_value[0]
        self.currenttotalPatternLength = self.spot_total_pattern_duration_spin_box_value[0]
        self.currentvideoFrameRate = self.video_frame_rate_value[0]
        ncurrentTotalFrame = math.trunc(self.currenttotalPatternLength / 1000 * self.currentvideoFrameRate)
        currentTotalSpotPatternInformation= self.totalSpotInformation
        backgroundColorBGR = self.spot_background_color

        self.TimeSequenceNSpotLocationdset = np.zeros((ncurrentTotalFrame,1+len(currentTotalSpotPatternInformation)),np.float32)
        self.spotImagedset = np.zeros((ncurrentTotalFrame,currentDisplayHeight,currentDisplayWidth,3), np.uint8)

        img = np.zeros((currentDisplayHeight,currentDisplayWidth,3), np.uint8)
        img[:,:,:] = backgroundColorBGR

        self.CheckOverTotalDuration(self.currenttotalPatternLength, currentTotalSpotPatternInformation, 11)

        for i in range(ncurrentTotalFrame):
            self.TimeSequenceNSpotLocationdset[i][0] = ('{:.3f}'.format(i / self.currentvideoFrameRate * 1000))
            self.spotImagedset[i] = img.copy()

        for i in range(len(currentTotalSpotPatternInformation)):
            if(((currentTotalSpotPatternInformation[i][4] == "vertical") and 
                (currentTotalSpotPatternInformation[i][6] == currentTotalSpotPatternInformation[i][8])) or 
                ((currentTotalSpotPatternInformation[i][4] == "horizontal") and 
                (currentTotalSpotPatternInformation[i][5] == currentTotalSpotPatternInformation[i][7]))):
                for j in range(ncurrentTotalFrame):
                    if(currentTotalSpotPatternInformation[i][4] == "vertical"):
                        self.TimeSequenceNSpotLocationdset[j,i+1] = currentTotalSpotPatternInformation[i][6]
                    else:
                        self.TimeSequenceNSpotLocationdset[j,i+1] = currentTotalSpotPatternInformation[i][5]
            elif(currentTotalSpotPatternInformation[i][9] == "sigmoid"):
                for j in range(ncurrentTotalFrame):
                    if(currentTotalSpotPatternInformation[i][4] == "vertical"):
                        self.TimeSequenceNSpotLocationdset[j,i+1] = self.sigmoidFunc(self.TimeSequenceNSpotLocationdset[j][0], 
                                                                                     currentTotalSpotPatternInformation[i][6], 
                                                                                     currentTotalSpotPatternInformation[i][8], 
                                                                                     currentTotalSpotPatternInformation[i][10], 
                                                                                     currentTotalSpotPatternInformation[i][11])
                    else:
                        self.TimeSequenceNSpotLocationdset[j,i+1] = self.sigmoidFunc(self.TimeSequenceNSpotLocationdset[j][0], 
                                                                                     currentTotalSpotPatternInformation[i][5], 
                                                                                     currentTotalSpotPatternInformation[i][7], 
                                                                                     currentTotalSpotPatternInformation[i][10], 
                                                                                     currentTotalSpotPatternInformation[i][11])
            else:
                for j in range(ncurrentTotalFrame):
                    if(currentTotalSpotPatternInformation[i][4] == "vertical"):
                        self.TimeSequenceNSpotLocationdset[j,i+1] = self.linearFunc(self.TimeSequenceNSpotLocationdset[j][0], 
                                                                                    currentTotalSpotPatternInformation[i][6], 
                                                                                    currentTotalSpotPatternInformation[i][8], 
                                                                                    currentTotalSpotPatternInformation[i][10], 
                                                                                    currentTotalSpotPatternInformation[i][11])
                    else:
                        self.TimeSequenceNSpotLocationdset[j,i+1] = self.linearFunc(self.TimeSequenceNSpotLocationdset[j][0], 
                                                                                    currentTotalSpotPatternInformation[i][5], 
                                                                                    currentTotalSpotPatternInformation[i][7], 
                                                                                    currentTotalSpotPatternInformation[i][10], 
                                                                                    currentTotalSpotPatternInformation[i][11])

        for i in range(len(currentTotalSpotPatternInformation)):
            spotColorBGR = currentTotalSpotPatternInformation[i][1]
            spotWidth = currentTotalSpotPatternInformation[i][2] 
            spotHeight = currentTotalSpotPatternInformation[i][3]
            spotHalfWidth = spotWidth // 2
            spotHalfHeight = spotHeight // 2
            spotInitialXPosition = currentTotalSpotPatternInformation[i][5]
            spotInitialYPosition = currentTotalSpotPatternInformation[i][6]

            if(currentTotalSpotPatternInformation[i][4] == "vertical"):
                for j in range(ncurrentTotalFrame):
                    self.spotImagedset[j] = cv2.rectangle(self.spotImagedset[j],
                                                          (spotInitialXPosition-spotHalfWidth-1,int(self.TimeSequenceNSpotLocationdset[j][i+1])-spotHalfHeight-1),
                                                          (spotInitialXPosition+spotHalfWidth-1,int(self.TimeSequenceNSpotLocationdset[j][i+1])+spotHalfHeight-1),
                                                          spotColorBGR,
                                                          -1)
            else:
                for j in range(ncurrentTotalFrame):
                    self.spotImagedset[j] = cv2.rectangle(self.spotImagedset[j],
                                                          (int(self.TimeSequenceNSpotLocationdset[j][i+1])-spotHalfWidth-1,spotInitialYPosition-spotHalfHeight-1),
                                                          (int(self.TimeSequenceNSpotLocationdset[j][i+1])+spotHalfWidth-1,spotInitialYPosition+spotHalfHeight-1),
                                                          spotColorBGR,
                                                          -1)
        
        self.spotImageArray = []
        self.spotQImageArray = []
        self.QPixmapArray = []

        for i in range(ncurrentTotalFrame):
            self.spotImageArray.append(Image.fromarray(self.spotImagedset[i]))
            self.spotQImageArray.append(qimage2ndarray.array2qimage(self.spotImagedset[i], normalize=False))
            self.QPixmapArray.append(QPixmap.fromImage(self.spotQImageArray[i]))

    def generateLoomingPattern(self):
        if(self.currentDiscCnt[0] == 0): return

        self.isPatternGenerated = True
        self.generatedPatternindex = 2

        currentDisplayHeight = self.displayer_height_value[0]
        currentDisplayWidth = self.displayer_width_value[0]
        self.currenttotalPatternLength = self.looming_total_pattern_duration_spin_box_value[0]
        currentDisplayCoveringAngle = self.looming_display_covering_angle_spin_box_value[0]
        self.currentvideoFrameRate = self.video_frame_rate_value[0]
        ncurrentTotalFrame = math.trunc(self.currenttotalPatternLength / 1000 * self.currentvideoFrameRate)
        currentTotalDiscPatternInformation= self.totalDiscInformation
        backgroundColorBGR = self.looming_background_color

        self.TimeSequenceNDiscLocationdset = np.zeros((ncurrentTotalFrame,1+len(currentTotalDiscPatternInformation)),np.float32)
        self.loomingImagedset = np.zeros((ncurrentTotalFrame,currentDisplayHeight,currentDisplayWidth,3), np.uint8)

        img = np.zeros((currentDisplayHeight,currentDisplayWidth,3), np.uint8)
        img[:,:,:] = backgroundColorBGR

        self.CheckOverTotalDuration(self.currenttotalPatternLength, currentTotalDiscPatternInformation, 7)

        for i in range(ncurrentTotalFrame):
            self.TimeSequenceNDiscLocationdset[i][0] = ('{:.3f}'.format(i / self.currentvideoFrameRate * 1000))
            self.loomingImagedset[i] = img.copy()

        for i in range(len(currentTotalDiscPatternInformation)):
            for j in range(ncurrentTotalFrame):
                self.TimeSequenceNDiscLocationdset[j,i+1] = self.atanFunc(self.TimeSequenceNDiscLocationdset[j][0], 
                                                                          currentTotalDiscPatternInformation[i][4], 
                                                                          currentTotalDiscPatternInformation[i][5], 
                                                                          currentTotalDiscPatternInformation[i][6], 
                                                                          currentTotalDiscPatternInformation[i][7])

        for i in range(len(currentTotalDiscPatternInformation)):
            discColorBGR = currentTotalDiscPatternInformation[i][1]
            discInitialXPosition = currentTotalDiscPatternInformation[i][2]
            discInitialYPosition = currentTotalDiscPatternInformation[i][3]

            for j in range(ncurrentTotalFrame):
                self.loomingImagedset[j] = cv2.circle(self.loomingImagedset[j],(discInitialXPosition-1, discInitialYPosition-1), 
                                                      int(currentDisplayHeight / currentDisplayCoveringAngle / 2 * self.TimeSequenceNDiscLocationdset[j][i+1]), 
                                                      discColorBGR,
                                                      -1)
                #print(int(currentDisplayHeight / currentDisplayCoveringAngle / 2 * self.TimeSequenceNDiscLocationdset[j][i+1]))

        self.loomingImageArray = []
        self.loomingQImageArray = []
        self.QPixmapArray = []

        for i in range(ncurrentTotalFrame):
            self.loomingImageArray.append(Image.fromarray(self.loomingImagedset[i]))
            self.loomingQImageArray.append(qimage2ndarray.array2qimage(self.loomingImagedset[i], normalize=False))
            self.QPixmapArray.append(QPixmap.fromImage(self.loomingQImageArray[i]))

    def generateGratingPattern(self):

        self.isPatternGenerated = True
        self.generatedPatternindex = 3

        currentDisplayHeight = self.displayer_height_value[0]
        currentDisplayWidth = self.displayer_width_value[0]
        self.currenttotalPatternLength = self.grating_total_pattern_duration_spin_box_value[0]
        self.currentvideoFrameRate = self.video_frame_rate_value[0]
        ncurrentTotalFrame = math.trunc(self.currenttotalPatternLength / 1000 * self.currentvideoFrameRate)
        backgroundColorBGR = self.grating_background_color
        gratingColorBGR = self.grating_color

        gratingMovementStartTiming = self.grating_movement_start_timing_spin_box_value[0]
        gratingMovementEndTiming = self.grating_movement_end_timing_spin_box_value[0]
        gratingLocationDifference = self.grating_location_difference_spin_box_value[0]

        directionOfTheGratingPos = "vertical" if self.grating_vertical_radio_button_value[0] == True else "horizontal"
        shapeOfTheGrating = "square" if self.grating_square_radio_button_value[0] == True else "sine"
        funcForTheGratingPos = "sigmoid" if self.grating_position_sigmoid_radio_button_value[0] == True else "linear"

        gratingCycleLength = self.grating_cycle_length_spin_box_value[0]
        gratingOrBackgroundLength = gratingCycleLength // 2
        gratingOrBackgroundHalfLength = gratingOrBackgroundLength // 2

        self.TimeSequenceNGratingLocationdset = np.zeros((ncurrentTotalFrame,2),np.float32)
        self.gratingImagedset = np.zeros((ncurrentTotalFrame,currentDisplayHeight,currentDisplayWidth,3), np.uint8)

        img = np.zeros((currentDisplayHeight,currentDisplayWidth,3), np.uint8)
        img[:,:,:] = backgroundColorBGR

        self.CheckOverTotalDuration(self.currenttotalPatternLength, [[gratingMovementEndTiming]], 0)

        for i in range(ncurrentTotalFrame):
            self.TimeSequenceNGratingLocationdset[i][0] = ('{:.3f}'.format(i / self.currentvideoFrameRate * 1000))
            self.gratingImagedset[i] = img.copy()


        if(funcForTheGratingPos == "sigmoid"):
            for i in range(ncurrentTotalFrame):
                if(directionOfTheGratingPos == "vertical"):
                    self.TimeSequenceNGratingLocationdset[i,1] = self.sigmoidFunc(self.TimeSequenceNGratingLocationdset[i][0], 
                                                                                  currentDisplayHeight//2, 
                                                                                  currentDisplayHeight//2 + gratingLocationDifference, 
                                                                                  gratingMovementStartTiming, 
                                                                                  gratingMovementEndTiming)
                else:
                    self.TimeSequenceNGratingLocationdset[i,1] = self.sigmoidFunc(self.TimeSequenceNGratingLocationdset[i][0], 
                                                                                  currentDisplayWidth//2, 
                                                                                  currentDisplayWidth//2 + gratingLocationDifference, 
                                                                                  gratingMovementStartTiming, 
                                                                                  gratingMovementEndTiming)
        else:
            for i in range(ncurrentTotalFrame):
                if(directionOfTheGratingPos == "vertical"):
                    self.TimeSequenceNGratingLocationdset[i,1] = self.linearFunc(self.TimeSequenceNGratingLocationdset[i][0], 
                                                                                 currentDisplayHeight//2, currentDisplayHeight//2 + 
                                                                                 gratingLocationDifference, gratingMovementStartTiming, 
                                                                                 gratingMovementEndTiming)
                else:
                    self.TimeSequenceNGratingLocationdset[i,1] = self.linearFunc(self.TimeSequenceNGratingLocationdset[i][0], 
                                                                                 currentDisplayWidth//2, currentDisplayWidth//2 + 
                                                                                 gratingLocationDifference, 
                                                                                 gratingMovementStartTiming, 
                                                                                 gratingMovementEndTiming)

        if(shapeOfTheGrating == "square"):
            if(directionOfTheGratingPos == "vertical"): #vertical
                if(gratingLocationDifference >= 0): #downward
                    for i in range(ncurrentTotalFrame):
                        if(self.TimeSequenceNGratingLocationdset[i,1] < currentDisplayHeight):
                            grating_midpoint_index_set = set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1), currentDisplayHeight+gratingCycleLength, gratingCycleLength)).union(set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1), -gratingCycleLength, -gratingCycleLength)))
                        else:
                            grating_midpoint_index_set = set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1), -gratingCycleLength, -gratingCycleLength)).intersection(set(range(-gratingCycleLength,currentDisplayHeight+gratingCycleLength)))
                        for j in grating_midpoint_index_set:
                            cv2.rectangle(self.gratingImagedset[i],(0,j-gratingOrBackgroundHalfLength),(currentDisplayWidth-1,j+gratingOrBackgroundHalfLength),gratingColorBGR,-1)
                else: #upward
                    for i in range(ncurrentTotalFrame):
                        if(self.TimeSequenceNGratingLocationdset[i,1] < currentDisplayHeight):
                            grating_midpoint_index_set = set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1), currentDisplayHeight+gratingCycleLength, gratingCycleLength)).union(set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1), -gratingCycleLength, -gratingCycleLength)))
                        else:
                            grating_midpoint_index_set = set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1),currentDisplayHeight+gratingCycleLength, gratingCycleLength)).intersection(set(range(-gratingCycleLength,currentDisplayHeight+gratingCycleLength)))
                        for j in grating_midpoint_index_set:
                            cv2.rectangle(self.gratingImagedset[i],(0,j-gratingOrBackgroundHalfLength),(currentDisplayWidth-1,j+gratingOrBackgroundHalfLength),gratingColorBGR,-1)
            else: #horizontal
                if(gratingLocationDifference >= 0): #rightward
                    for i in range(ncurrentTotalFrame):
                        if(self.TimeSequenceNGratingLocationdset[i,1] < currentDisplayWidth):
                            grating_midpoint_index_set = set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1), currentDisplayWidth+gratingCycleLength, gratingCycleLength)).union(set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1), -gratingCycleLength, -gratingCycleLength)))
                        else:
                            grating_midpoint_index_set = set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1),-gratingCycleLength, -gratingCycleLength)).intersection(set(range(-gratingCycleLength,currentDisplayWidth+gratingCycleLength)))
                        for j in grating_midpoint_index_set:
                            cv2.rectangle(self.gratingImagedset[i],(j-gratingOrBackgroundHalfLength,0),(j+gratingOrBackgroundHalfLength,currentDisplayHeight-1),gratingColorBGR,-1)
                else: #leftward
                    for i in range(ncurrentTotalFrame):
                        if(self.TimeSequenceNGratingLocationdset[i,1] < currentDisplayWidth):
                            grating_midpoint_index_set = set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1), currentDisplayWidth+gratingCycleLength, gratingCycleLength)).union(set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1), -gratingCycleLength, -gratingCycleLength)))
                        else:
                            grating_midpoint_index_set = set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1), currentDisplayWidth+gratingCycleLength, gratingCycleLength)).intersection(set(range(-gratingCycleLength,currentDisplayWidth+gratingCycleLength)))
                        for j in grating_midpoint_index_set:
                            cv2.rectangle(self.gratingImagedset[i],(j-gratingOrBackgroundHalfLength,0),(j+gratingOrBackgroundHalfLength,currentDisplayHeight-1),gratingColorBGR,-1)

        else: #sine
            if(directionOfTheGratingPos == "vertical"): #vertical
                if(gratingLocationDifference >= 0): #downward
                    for i in range(ncurrentTotalFrame):
                        if(self.TimeSequenceNGratingLocationdset[i,1] < currentDisplayHeight):
                            grating_midpoint_index_set = set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1), currentDisplayHeight+gratingCycleLength, gratingCycleLength)).union(set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1), -gratingCycleLength, -gratingCycleLength)))
                        else:
                            grating_midpoint_index_set = set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1), -gratingCycleLength, -gratingCycleLength)).intersection(set(range(-gratingCycleLength,currentDisplayHeight+gratingCycleLength)))
                        for j in grating_midpoint_index_set:
                            for k in range(gratingOrBackgroundLength-1,-1,-1):
                                blueColor = gratingColorBGR[0] + k / gratingOrBackgroundLength * (backgroundColorBGR[0] - gratingColorBGR[0])
                                greenColor = gratingColorBGR[1] + k / gratingOrBackgroundLength * (backgroundColorBGR[1] - gratingColorBGR[1])
                                redColor = gratingColorBGR[2] + k / gratingOrBackgroundLength * (backgroundColorBGR[2] - gratingColorBGR[2])
                                #print([blueColor,greenColor,redColor])
                                cv2.rectangle(self.gratingImagedset[i],(0,j-k),(currentDisplayWidth-1,j+k),[int(blueColor),int(greenColor),int(redColor)],-1)
                else: #upward
                    for i in range(ncurrentTotalFrame):
                        if(self.TimeSequenceNGratingLocationdset[i,1] < currentDisplayHeight):
                            grating_midpoint_index_set = set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1), currentDisplayHeight+gratingCycleLength, gratingCycleLength)).union(set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1), -gratingCycleLength, -gratingCycleLength)))
                        else:
                            grating_midpoint_index_set = set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1),currentDisplayHeight+gratingCycleLength, gratingCycleLength)).intersection(set(range(-gratingCycleLength,currentDisplayHeight+gratingCycleLength)))
                        for j in grating_midpoint_index_set:
                            for k in range(gratingOrBackgroundLength-1,-1,-1):
                                blueColor = gratingColorBGR[0] + k / gratingOrBackgroundLength * (backgroundColorBGR[0] - gratingColorBGR[0])
                                greenColor = gratingColorBGR[1] + k / gratingOrBackgroundLength * (backgroundColorBGR[1] - gratingColorBGR[1])
                                redColor = gratingColorBGR[2] + k / gratingOrBackgroundLength * (backgroundColorBGR[2] - gratingColorBGR[2])
                                cv2.rectangle(self.gratingImagedset[i],(0,j-k),(currentDisplayWidth-1,j+k),[blueColor,greenColor,redColor],-1)
            else: #horizontal
                if(gratingLocationDifference >= 0): #rightward
                    for i in range(ncurrentTotalFrame):
                        if(self.TimeSequenceNGratingLocationdset[i,1] < currentDisplayWidth):
                            grating_midpoint_index_set = set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1), currentDisplayWidth+gratingCycleLength, gratingCycleLength)).union(set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1), -gratingCycleLength, -gratingCycleLength)))
                        else:
                            grating_midpoint_index_set = set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1),-gratingCycleLength, -gratingCycleLength)).intersection(set(range(-gratingCycleLength,currentDisplayWidth+gratingCycleLength)))
                        for j in grating_midpoint_index_set:
                            for k in range(gratingOrBackgroundLength-1,-1,-1):
                                blueColor = gratingColorBGR[0] + k / gratingOrBackgroundLength * (backgroundColorBGR[0] - gratingColorBGR[0])
                                greenColor = gratingColorBGR[1] + k / gratingOrBackgroundLength * (backgroundColorBGR[1] - gratingColorBGR[1])
                                redColor = gratingColorBGR[2] + k / gratingOrBackgroundLength * (backgroundColorBGR[2] - gratingColorBGR[2])
                                cv2.rectangle(self.gratingImagedset[i],(j-k,0),(j+k,currentDisplayHeight-1),[blueColor,greenColor,redColor],-1)
                else: #leftward
                    for i in range(ncurrentTotalFrame):
                        if(self.TimeSequenceNGratingLocationdset[i,1] < currentDisplayWidth):
                            grating_midpoint_index_set = set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1), currentDisplayWidth+gratingCycleLength, gratingCycleLength)).union(set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1), -gratingCycleLength, -gratingCycleLength)))
                        else:
                            grating_midpoint_index_set = set(range(int(self.TimeSequenceNGratingLocationdset[i,1]-1), currentDisplayWidth+gratingCycleLength, gratingCycleLength)).intersection(set(range(-gratingCycleLength,currentDisplayWidth+gratingCycleLength)))
                        for j in grating_midpoint_index_set:
                            for k in range(gratingOrBackgroundLength-1,-1,-1):
                                blueColor = gratingColorBGR[0] + k / gratingOrBackgroundLength * (backgroundColorBGR[0] - gratingColorBGR[0])
                                greenColor = gratingColorBGR[1] + k / gratingOrBackgroundLength * (backgroundColorBGR[1] - gratingColorBGR[1])
                                redColor = gratingColorBGR[2] + k / gratingOrBackgroundLength * (backgroundColorBGR[2] - gratingColorBGR[2])
                                cv2.rectangle(self.gratingImagedset[i],(j-k,0),(j+k,currentDisplayHeight-1),[blueColor,greenColor,redColor],-1)

        self.gratingImageArray = []
        self.gratingQImageArray = []
        self.QPixmapArray = []

        for i in range(ncurrentTotalFrame):
            self.gratingImageArray.append(Image.fromarray(self.gratingImagedset[i]))
            self.gratingQImageArray.append(qimage2ndarray.array2qimage(self.gratingImagedset[i], normalize=False))
            self.QPixmapArray.append(QPixmap.fromImage(self.gratingQImageArray[i]))

        self.gratingImagedsetforHDF = np.flip(self.gratingImagedset, axis = 3)



    def CheckOverTotalDuration(self, total_pattern_duration, elements_info, endtime_idx):
        over_endtime_flag = False
        for element in elements_info:
            if element[endtime_idx] > total_pattern_duration :
                over_endtime_flag = True
        
        if over_endtime_flag :
            self.OverTotalDuration()

    def OverTotalDuration(self):
        # edit OverTotalDuration meesage
        button_reply = QMessageBox.information(self, 'Over Title', 'Message') # <- here
        
        """
        # if need reply, use this 
        button_reply = QMessageBox.information(self, 'OverOverOver', 'Message', QMessageBox.Yes | QMessageBox.Save | ... add somethin ) # <- here
        if button_reply == QMessageBox.Yes:
            do something ...
        elif button_reply == QMessageBox.Save:
        """



    def linearFunc(self, currenttime, initpos, finpos, inittime, fintime):
        dt = fintime - inittime
        dp = finpos - initpos
        midtime = inittime + (dt/2)

        if(dp > 0):
            if(currenttime < inittime):
                linearval = initpos
            elif(currenttime < midtime):
                linearval = math.floor( dp / dt * (currenttime - inittime) + initpos)
            elif(currenttime < fintime):
                linearval = math.ceil( dp / dt * (currenttime - inittime) + initpos)
            else:
                linearval = finpos
        else:
            if(currenttime < inittime):
                linearval = initpos
            elif(currenttime < midtime):
                linearval = math.ceil( dp / dt * (currenttime - inittime) + initpos)
            elif(currenttime < fintime):
                linearval = math.floor( dp / dt * (currenttime - inittime) + initpos)
            else:
                linearval = finpos

        return linearval

    def sigmoidFunc(self, currenttime, initpos, finpos, inittime, fintime):
        dt = fintime - inittime
        dp = finpos - initpos
        alphaval = self.getSigmoidAlphaValue(dt,dp,0.9)
        midtime = inittime + (dt/2)
        #print(dt, dp, alphaval, midtime)
        if(dp > 0):
            if (currenttime < midtime):
                sigmoidval = math.floor( dp / (1 + np.exp(-alphaval * (currenttime - midtime))) + initpos)
            else:
                sigmoidval = math.ceil( dp / (1 + np.exp(-alphaval * (currenttime - midtime))) + initpos)
        else:
            if (currenttime < midtime):
                sigmoidval = math.ceil( dp / (1 + np.exp(-alphaval * (currenttime - midtime))) + initpos)
            else:
                sigmoidval = math.floor( dp / (1 + np.exp(-alphaval * (currenttime - midtime))) + initpos)

        return sigmoidval

    def atanFunc(self, currenttime, initpos, finpos, inittime, fintime):
        
        if(currenttime < inittime):
            atanval = initpos
        elif(currenttime > fintime):
            atanval = finpos
        else:
            dt = fintime - inittime
            beta = self.getAtanBetaValue(dt, initpos, finpos)
            alpha = self.getAtanAlphaValue(initpos, beta)
            atanval = 2 * 180 / math.pi * math.atan(alpha / (beta - (currenttime - inittime)))

            if(atanval < initpos):
                atanval = initpos
            elif(atanval > finpos):
                atanval = finpos

        return atanval

    def getAtanBetaValue(self, dt, initpos, finpos):
        return dt * math.tan((math.pi / 180) * finpos / 2) / (math.tan((math.pi / 180) * finpos / 2) - math.tan((math.pi / 180) * initpos / 2))

    def getAtanAlphaValue(self, initpos, beta):
        return math.tan((math.pi / 180) * initpos / 2) * beta

    def getSigmoidAlphaValue(self, dt, dp, uval):
        return 2 / dt * (np.log((abs(dp)/uval)-1))

    def saveActivatedTab(self):
        self.currentActivatedTabIndex = self.pattern_type_tab.currentIndex()
    
    def saveActivatedGeneratorTab(self):
        self.currentActivatedGeneratorTabIndex = self.generator_type_tab.currentIndex()

    def createSizeNFrameRateGroupBoxFormLayout(self):
        sizeNFrameRateGroupBoxFormLayout = QFormLayout()

        self.displayer_width_spin_box = QSpinBox()
        self.displayer_width_spin_box.setMinimum(1)
        self.displayer_width_spin_box.setMaximum(DEFAULTDISPLAYERWIDTHRANGE)
        self.displayer_width_spin_box.setValue(DEFAULTDISPLAYERWIDTH)
        self.displayer_width_value = [0]
        self.saveSpinBoxValue(self.displayer_width_spin_box, self.displayer_width_value)
        self.displayer_width_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.displayer_width_spin_box, self.displayer_width_value))
        self.displayer_width_spin_box.valueChanged.connect(lambda : self.changeBarRange())
        self.displayer_width_spin_box.valueChanged.connect(lambda : self.changeSpotWidthRange())
        self.displayer_width_spin_box.valueChanged.connect(lambda : self.changeGratingRange())


        self.displayer_height_spin_box = QSpinBox()
        self.displayer_height_spin_box.setMinimum(1)
        self.displayer_height_spin_box.setMaximum(DEFAULTDISPLAYERHEIGHTRANGE)
        self.displayer_height_spin_box.setValue(DEFAULTDISPLAYERHEIGHT)
        self.displayer_height_value = [0]
        self.saveSpinBoxValue(self.displayer_height_spin_box, self.displayer_height_value)
        self.displayer_height_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.displayer_height_spin_box, self.displayer_height_value))
        self.displayer_height_spin_box.valueChanged.connect(lambda : self.changeBarRange())
        self.displayer_width_spin_box.valueChanged.connect(lambda : self.changeSpotHeightRange())
        self.displayer_width_spin_box.valueChanged.connect(lambda : self.changeGratingRange())


        self.video_frame_rate_spin_box = QSpinBox()
        self.video_frame_rate_spin_box.setMinimum(1)
        self.video_frame_rate_spin_box.setMaximum(DEFAULTFRAMERATERANGE)
        self.video_frame_rate_spin_box.setValue(DEFAULTFRAMERATE)
        self.video_frame_rate_value = [0]
        self.saveSpinBoxValue(self.video_frame_rate_spin_box, self.video_frame_rate_value)
        self.video_frame_rate_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.video_frame_rate_spin_box, self.video_frame_rate_value))

        #need default value

        sizeNFrameRateGroupBoxFormLayout.addRow("displayer width : ", self.displayer_width_spin_box)
        sizeNFrameRateGroupBoxFormLayout.addRow("displayer height : ", self.displayer_height_spin_box)
        sizeNFrameRateGroupBoxFormLayout.addRow("video frame rate : ", self.video_frame_rate_spin_box)

        return sizeNFrameRateGroupBoxFormLayout
    
    def clickedRadioButton(self, button):
        button_text = self.rotationGroup.checkedButton().text()
        if button_text == "0°":
            self.checked_rotate_degree = 0
            return
        if button_text == "90°":
            self.checked_rotate_degree = 90
            return
        if button_text == "180°":
            self.checked_rotate_degree = 180
            return
        if button_text == "270°":
            self.checked_rotate_degree = 270
            return
        
        return

    def createRotationRadioBox(self):
        
        
        # rotation_label = QLabel("Video roation : ")
        # self.rotationBoxLayout.addWidget(rotation_label)
        
        self.rotationGroup = QButtonGroup(self.rotationGroupBox)
        
        hbox0 = QHBoxLayout()
        self.radio_0 = QRadioButton("0°", self.rotationGroupBox)
        self.label_0 = QLabel()
        self.label_0.setFixedSize(30,30)
        self.label_0.setScaledContents(True)
        self.label_0.setMinimumSize(1, 1)
        pixmap0 = QPixmap('./image_90.png')
        self.label_0.setPixmap(pixmap0)
        hbox0.addWidget(self.radio_0)
        hbox0.setSpacing(1)
        hbox0.addWidget(self.label_0)
        
        hbox90 = QHBoxLayout()
        self.radio_90 = QRadioButton("90°", self.rotationGroupBox)
        self.label_90 = QLabel()
        
        
        self.label_90.setFixedSize(30,30)
        self.label_90.setScaledContents(True)
        self.label_90.setMinimumSize(1, 1)
        pixmap90 = QPixmap('./image_90.png').scaled(30,30)
        self.label_90.setPixmap(pixmap90)
        hbox90.addWidget(self.radio_90)
        hbox90.setSpacing(1)
        hbox90.addWidget(self.label_90)
        
        
        
        hbox180 = QHBoxLayout()
        self.radio_180 = QRadioButton("180°", self.rotationGroupBox)
        self.label_180 = QLabel()
        self.label_180.setFixedSize(30,30)
        self.label_180.setScaledContents(True)
        self.label_180.setMinimumSize(1, 1)
        pixmap180 = QPixmap('./image_90.png')
        self.label_180.setPixmap(pixmap180)
        hbox180.addWidget(self.radio_180)
        hbox180.setSpacing(1)
        hbox180.addWidget(self.label_180)
        
        
        hbox270 = QHBoxLayout()
        self.radio_270 = QRadioButton("270°", self.rotationGroupBox)
        self.label_270 = QLabel()
        self.label_270.setFixedSize(30,30)
        self.label_270.setScaledContents(True)
        self.label_270.setMinimumSize(1, 1)
        pixmap270 = QPixmap('./image_90.png')
        self.label_270.setPixmap(pixmap270)
        hbox270.addWidget(self.radio_270)
        hbox270.setSpacing(1)
        hbox270.addWidget(self.label_270)
        
        
        
        
        # self.checked_rotate_degree 변수에 선택된 각도(호도법, °) 저장
        self.checked_rotate_degree = 0
        self.rotationGroup.addButton(self.radio_0)
        self.rotationGroup.addButton(self.radio_90)
        self.rotationGroup.addButton(self.radio_180)
        self.rotationGroup.addButton(self.radio_270)
        self.rotationGroup.buttonClicked.connect(self.clickedRadioButton)
        
        self.rotation_button_hbox = QHBoxLayout()
        
        spacing_px = 50
        self.rotation_button_hbox.addStretch(0)
        self.rotation_button_hbox.addLayout(hbox0)
        self.rotation_button_hbox.addStretch(0)
        self.rotation_button_hbox.addLayout(hbox90)
        self.rotation_button_hbox.addStretch(0)
        self.rotation_button_hbox.addLayout(hbox180)
        self.rotation_button_hbox.addStretch(0)
        self.rotation_button_hbox.addLayout(hbox270)
        self.rotation_button_hbox.addStretch(0)
        
        
        self.rotationBoxLayout.addLayout(self.rotation_button_hbox)
        self.radio_0.setChecked(True)
        
        
        return
        
    def createVideoTab(self):
        self.videoGenerateLayout = QVBoxLayout()

        # add input & output path
        
        pathFormLayout = self.createVideoFormLayout()
        
        self.videoPathGroupBox = QGroupBox('File path')
        self.videoPathGroupBox.setFixedHeight(100)
        self.videoPathGroupBox.setLayout(pathFormLayout)
        self.videoGenerateLayout.addWidget(self.videoPathGroupBox)
        
        self.rotationBoxLayout = QHBoxLayout()
        self.rotationGroupBox = QGroupBox('Roation')
        self.rotationGroupBox.setFixedHeight(50)
        self.rotationGroupBox.setLayout(self.rotationBoxLayout)
        self.videoGenerateLayout.addWidget(self.rotationGroupBox)
        self.createRotationRadioBox()

        # add image label
        
        self.previewImageGroupBox = QGroupBox('Preview image')
        self.previewImageContentLayout = QVBoxLayout()
        self.previewImageLabel = QLabel()#PixmapLabel(self.previewImageGroupBox)

        
        self.previewImageContentLayout.addWidget(self.previewImageLabel)
        self.previewImageGroupBox.setLayout(self.previewImageContentLayout)
        self.videoGenerateLayout.addWidget(self.previewImageGroupBox)

        self.videoTapButtonLayout = QVBoxLayout()
        self.video_tap_generate_push_button = QPushButton("Generate Video")
        self.video_tap_generate_push_button.setFixedHeight(30)
        self.video_tap_generate_push_button.setFont(QFont("Arial", 13, QFont.Bold, italic=False))
        self.video_tap_generate_push_button.clicked.connect(self.runVideoConverter)
        

        self.videoTapButtonLayout.addWidget(self.video_tap_generate_push_button)

        self.videoGenerateLayout.addLayout(self.videoTapButtonLayout)

        
        

        widget = QWidget()
        widget.setLayout(self.videoGenerateLayout)
        return widget



    def createVideoFormLayout(self):
        pathFormLayout = QFormLayout()
        
        input_video_path_layout, self.input_video_line_edit, self.input_video_push_button = self.pathLineEditLayout('input')
        output_video_path_layout, self.output_video_line_edit, self.input_video_push_button = self.pathLineEditLayout('output')
        
        pathFormLayout.addRow("Input video file  ", input_video_path_layout)
        pathFormLayout.addRow("Output video file ", output_video_path_layout)

        return pathFormLayout

    def pathLineEditLayout(self, type):
        hboxlayout = QHBoxLayout()
        video_path_line_edit = QLineEdit()
        video_path_line_edit.setReadOnly(True)
        video_path_line_edit.setReadOnly(True)
        video_push_button = QPushButton("...")
        if type=='input':
            self.input_video_file_path = ""
            video_push_button.clicked.connect(lambda : self.openVideoFilePath(video_path_line_edit))
        elif type=='output':
            self.output_video_file_path = ""
            video_push_button.clicked.connect(lambda : self.saveVideoFilePath(video_path_line_edit))
        hboxlayout.addWidget(video_path_line_edit)
        hboxlayout.addWidget(video_push_button)

        return hboxlayout, video_path_line_edit, video_push_button

    def openVideoFilePath(self,path_line_edit):
        path = QFileDialog.getOpenFileName(self, '','','Video file (*.mp4)')
        # does not select file
        if not path[0]:
            return
        
        filename, file_extension = os.path.splitext(path[0])
        path_line_edit.setText(path[0])
        self.input_video_file_path = path[0]
        if not file_extension == '.mp4':
            # do something if file extension is not .mp4
            return

        # previewImage = self.getPreviewImage(path[0])
        #img = Image.fromarray(previewImage)

        #self.input_video_file_path = ""

        vidcap = cv2.VideoCapture(self.input_video_file_path)
        # get total number of frames
        totalFrames = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
        # set frame position
        vidcap.set(cv2.CAP_PROP_POS_FRAMES,totalFrames//2)
        success, image = vidcap.read()
        if success:
            cv2.imwrite("random_frame.jpg", image)

        h,w,c = image.shape
        bpl = 3 * w
        qimg = QImage(image.data, w, h, bpl, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(qimg)

        self.previewImageLabel.setPixmap(pixmap)

        self.previewImageLabel.resize(self.previewImageGroupBox.width(),self.previewImageGroupBox.height())
        self.previewImageLabel.setScaledContents(True)
        self.previewImageLabel.setMinimumSize(1, 1)
        self.previewImageContentLayout.addWidget(self.previewImageLabel)

    def runVideoConverter(self):
        if self.input_video_file_path == "" or self.output_video_file_path == "":
            return
        self.progressDialog = QProgressDialog("Starting...", "Cancel", 0, 100, self)
        self.progressDialog.setWindowTitle('Please wait...')
        self.progressDialog.setModal(True)
        self.progressDialog.show()
        self.progressDialog.canceled.connect(self.stop_conversion)
        
        self.thread = convertVideoThread(self.input_video_file_path, self.output_video_file_path)
        self.thread.update_progress.connect(self.updateProgress)
        self.thread.start()
        self.thread.finished.connect(self.conversion_finished)
        
        #converVideo(self.input_video_file_path, self.output_video_file_path, self.progressDialog, QApplication.processEvents)

    def updateProgress(self, value):
        self.progressDialog.setValue(value)
        
    def conversion_finished(self):
        self.progressDialog.close()
        return
    
    def stop_conversion(self):
        self.thread.stop()
        return
        

    def saveVideoFilePath(self, path_line_edit):
        path =  QFileDialog.getSaveFileName(self, 'Save file', "","Video file (*.mp4)") 
        if not path[0]:
            return
        path_line_edit.setText(path[0])
        self.output_video_file_path = path[0]

    def createPatternTab(self):
        patternGenerateLayout = QVBoxLayout()
        firstRowLayout = QHBoxLayout()
        secondRowLayout = QHBoxLayout()
        thirdRowLayout = QVBoxLayout()
        
        #designing firstRowLayout
        
        size_n_frame_rate_group_box = QGroupBox('Displayer size and Video frame rate')
        size_n_frame_rate_group_box.setLayout(self.createSizeNFrameRateGroupBoxFormLayout())

        firstRowLayout.addWidget(size_n_frame_rate_group_box)

        #designing secondRowLayout

        self.pattern_type_tab = QTabWidget()

        stylesheet = """ 
            QTabWidget>QWidget>QWidget{background: rgb(240,240,240);}
            """
        self.pattern_type_tab.setStyleSheet(stylesheet)

        barTab = self.createBarTab()
        spotTab = self.createSpotTab()
        loomingTab = self.createLoomingTab()
        gratingTab = self.createGratingTab()

        self.currentActivatedTabIndex = 0
        self.pattern_type_tab.currentChanged.connect(lambda : self.saveActivatedTab())

        self.pattern_type_tab.addTab(barTab,"Bar")
        self.pattern_type_tab.addTab(spotTab,"Spot")
        self.pattern_type_tab.addTab(loomingTab, "Looming")
        self.pattern_type_tab.addTab(gratingTab, "Grating")


        secondRowLayout.addWidget(self.pattern_type_tab)

        self.isPatternGenerated = False
        self.generatedPatternindex = -1

        self.generate_pattern_push_button = QPushButton('Generate Pattern')
        self.generate_pattern_push_button.setFixedHeight(30)
        self.generate_pattern_push_button.setFont(QFont("Arial", 13, QFont.Bold, italic=False))
        self.generate_pattern_push_button.clicked.connect(lambda : self.generatePattern())

        self.show_generated_pattern_push_button = QPushButton('Show Generated Pattern')
        self.show_generated_pattern_push_button.setFixedHeight(30)
        self.show_generated_pattern_push_button.setFont(QFont("Arial", 13, QFont.Bold, italic=False))
        self.show_generated_pattern_push_button.clicked.connect(lambda : self.showGeneratedPattern())

        self.saveDataRowLayout = QHBoxLayout()

        self.save_generated_pattern_as_hdf_push_button = QPushButton('Save as h5')
        self.save_generated_pattern_as_hdf_push_button.setFixedHeight(30)
        self.save_generated_pattern_as_hdf_push_button.setFont(QFont("Arial", 13, QFont.Bold, italic=False))
        self.save_generated_pattern_as_hdf_push_button.clicked.connect(lambda : self.saveGeneratedPatternasHDF())


        self.save_generated_pattern_as_sequential_image_push_button = QPushButton('Save as mp4')
        self.save_generated_pattern_as_sequential_image_push_button.setFixedHeight(30)
        self.save_generated_pattern_as_sequential_image_push_button.setFont(QFont("Arial", 13, QFont.Bold, italic=False))
        self.save_generated_pattern_as_sequential_image_push_button.clicked.connect(lambda : self.saveGeneratedPatternasSequentialImage())

        self.save_generated_pattern_as_gif_push_button = QPushButton('Save as gif')
        self.save_generated_pattern_as_gif_push_button.setFixedHeight(30)
        self.save_generated_pattern_as_gif_push_button.setFont(QFont("Arial", 13, QFont.Bold, italic=False))
        self.save_generated_pattern_as_gif_push_button.clicked.connect(lambda : self.saveGeneratedPatternasGIF())

        self.saveDataRowLayout.addWidget(self.save_generated_pattern_as_hdf_push_button)
        self.saveDataRowLayout.addWidget(self.save_generated_pattern_as_sequential_image_push_button)
        self.saveDataRowLayout.addWidget(self.save_generated_pattern_as_gif_push_button)

        thirdRowLayout.addWidget(self.generate_pattern_push_button)
        thirdRowLayout.addWidget(self.show_generated_pattern_push_button)
        thirdRowLayout.addLayout(self.saveDataRowLayout)

        patternGenerateLayout.addLayout(firstRowLayout)
        patternGenerateLayout.addLayout(secondRowLayout)
        patternGenerateLayout.addLayout(thirdRowLayout)
        #self.generatorLayout.addLayout(patternGenerateLayout)


        widget = QWidget()
        widget.setLayout(patternGenerateLayout)

        return widget

    def createBarTab(self):
        mainvbox = QVBoxLayout()

        barGroupBox = QGroupBox('bar information')

        barFundamentalForm, barForm, = self.createBarTabFormLayout()

        self.addbarpushbutton = QPushButton('Add Bar')
        self.addBarPushButtonLayout = self.createAddORDeleteObjectPushButtonLayout(self.addbarpushbutton)

        self.currentBarCnt = [0]
        self.totalBarInformation = []
        self.barCheckBoxList = []

        self.addbarpushbutton.clicked.connect(lambda : self.saveNAddData("Bar", self.currentBarCnt, self.totalBarInformation, self.bar_table, self.barCheckBoxList))

        bar_index = [" ","Bar #", "Bar \ncolor","Bar \nwidth","Dir of \nthe bar pos","Initial bar \nmid pos", "Final bar \nmid pos","Func of \nthe bar pos","Start t of \nthe bar mov","End t of \nthe bar mov"]

        self.bar_table = QTableWidget()
        self.bar_table.setRowCount(1)
        self.bar_table.setColumnCount(len(bar_index))

        self.bar_table.verticalHeader().setVisible(False)
        self.bar_table.horizontalHeader().setVisible(False)


        #self.bar_table.horizontalHeader().setDefaultSectionSize(10)
        self.bar_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.bar_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.bar_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        self.bar_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)

        for i in range(len(bar_index)):
            self.bar_table.setItem(0, i, QTableWidgetItem(bar_index[i]))
            firstRowItem = self.bar_table.item(0,i)
            firstRowItem.setFont(QFont("Arial", 7, QFont.Bold, italic=False))
            firstRowItem.setTextAlignment(Qt.AlignCenter)
            firstRowItem.setBackground(QColor(200,200,200))


        self.deletebarpushbutton = QPushButton('Delete Selected Bar')
        self.deleteBarPushButtonLayout = self.createAddORDeleteObjectPushButtonLayout(self.deletebarpushbutton)

        self.barCheckBoxValueList = []

        self.deletebarpushbutton.clicked.connect(lambda : self.deleteRowData(self.barCheckBoxList,self.currentBarCnt,self.barCheckBoxValueList,self.bar_table,self.totalBarInformation, 1))


        barVbox = QVBoxLayout()
        barVbox.addLayout(barForm)
        barVbox.addLayout(self.addBarPushButtonLayout)


        barGroupBox.setLayout(barVbox)

        mainvbox.addLayout(barFundamentalForm)
        mainvbox.addWidget(barGroupBox)
        mainvbox.addWidget(self.bar_table)
        mainvbox.addLayout(self.deleteBarPushButtonLayout)
        #mainvbox.setStretch(0,1)
        #mainvbox.setStretch(1,5)


        widget = QWidget()
        widget.setLayout(mainvbox)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(widget)
        scroll_area.setWidgetResizable(True)
        return scroll_area

    def createAddORDeleteObjectPushButtonLayout(self, pushbutton):
        label1 = QLabel('')
        label2 = QLabel('')
        pushbutton.setFixedHeight(30)

        layout = QHBoxLayout()
        layout.addWidget(label1)
        layout.addWidget(label2)
        layout.addWidget(pushbutton)

        return layout

    def createSpotTab(self):
        mainvbox = QVBoxLayout()

        spotGroupBox = QGroupBox('spot information')

        spotFundamentalForm, spotForm= self.createSpotTabFormLayout()

        self.addspotpushbutton = QPushButton('Add Spot')
        self.addSpotPushButtonLayout = self.createAddORDeleteObjectPushButtonLayout(self.addspotpushbutton)

        self.currentSpotCnt = [0]
        self.totalSpotInformation = []
        self.spotCheckBoxList = []

        self.addspotpushbutton.clicked.connect(lambda : self.saveNAddData("Spot", self.currentSpotCnt, self.totalSpotInformation, self.spot_table, self.spotCheckBoxList))

        spot_index = [" ","Spot #", "Spot \ncolor","Spot \nwidth","Spot \nheight","Dir of \nthe spot pos","Initial spot \nmid x pos", "Initial spot \nmid y pos","Final spot \nmid x pos","Final spot \nmid y pos","Func of \nthe spot pos","Start t of \nthe spot mov","End t of \nthe spot mov"]

        self.spot_table = QTableWidget()
        self.spot_table.setRowCount(1)
        self.spot_table.setColumnCount(len(spot_index))

        self.spot_table.verticalHeader().setVisible(False)
        self.spot_table.horizontalHeader().setVisible(False)


        #self.bar_table.horizontalHeader().setDefaultSectionSize(10)
        self.spot_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.spot_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.spot_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        self.spot_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)



        for i in range(len(spot_index)):
            self.spot_table.setItem(0, i, QTableWidgetItem(spot_index[i]))
            firstRowItem = self.spot_table.item(0,i)
            firstRowItem.setFont(QFont("Arial", 6, QFont.Bold, italic=False))
            firstRowItem.setTextAlignment(Qt.AlignCenter)
            firstRowItem.setBackground(QColor(200,200,200))


        self.deletespotpushbutton = QPushButton('Delete Selected Spot')
        self.deleteSpotPushButtonLayout = self.createAddORDeleteObjectPushButtonLayout(self.deletespotpushbutton)

        self.spotCheckBoxValueList = []


        self.deletespotpushbutton.clicked.connect(lambda : self.deleteRowData(self.spotCheckBoxList,self.currentSpotCnt,self.spotCheckBoxValueList,self.spot_table,self.totalSpotInformation, 1))


        spotVbox = QVBoxLayout()
        spotVbox.addLayout(spotForm)
        spotVbox.addLayout(self.addSpotPushButtonLayout)


        spotGroupBox.setLayout(spotVbox)

        mainvbox.addLayout(spotFundamentalForm)
        mainvbox.addWidget(spotGroupBox)
        mainvbox.addWidget(self.spot_table)
        mainvbox.addLayout(self.deleteSpotPushButtonLayout)
        #mainvbox.setStretch(0,1)
        #mainvbox.setStretch(1,5)


        widget = QWidget()
        widget.setLayout(mainvbox)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(widget)
        scroll_area.setWidgetResizable(True)
        return scroll_area


    def createLoomingTab(self):
        mainvbox = QVBoxLayout()

        discGroupBox = QGroupBox('disc information')

        loomingFundamentalForm, discForm = self.createLoomingTabFormLayout()

        self.add_disc_push_button = QPushButton('Add Disc')
        self.addDiscPushButtonLayout = self.createAddORDeleteObjectPushButtonLayout(self.add_disc_push_button)

        self.currentDiscCnt = [0]
        self.totalDiscInformation = []
        self.discCheckBoxList = []

        self.add_disc_push_button.clicked.connect(lambda : self.saveNAddData("Disc", self.currentDiscCnt, self.totalDiscInformation, self.disc_table, self.discCheckBoxList))

        disc_index = [" ","Disc #", "Disc \ncolor","Disc \nx pos","Disc \ny pos","Initial bar \nradius", "Final bar \nradius","Start t of \nthe disc mov","End t of \nthe disc mov"]

        self.disc_table = QTableWidget()
        self.disc_table.setRowCount(1)
        self.disc_table.setColumnCount(len(disc_index))

        self.disc_table.verticalHeader().setVisible(False)
        self.disc_table.horizontalHeader().setVisible(False)

        #self.bar_table.horizontalHeader().setDefaultSectionSize(10)
        self.disc_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.disc_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.disc_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        self.disc_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)

        for i in range(len(disc_index)):
            self.disc_table.setItem(0, i, QTableWidgetItem(disc_index[i]))
            firstRowItem = self.disc_table.item(0,i)
            firstRowItem.setFont(QFont("Arial", 7, QFont.Bold, italic=False))
            firstRowItem.setTextAlignment(Qt.AlignCenter)
            firstRowItem.setBackground(QColor(200,200,200))

        self.delete_disc_push_button = QPushButton('Delete Selected Disc')
        self.deleteDiscPushButtonLayout = self.createAddORDeleteObjectPushButtonLayout(self.delete_disc_push_button)

        self.discCheckBoxValueList = []

        self.delete_disc_push_button.clicked.connect(lambda : self.deleteRowData(self.discCheckBoxList,self.currentDiscCnt,self.discCheckBoxValueList,self.disc_table,self.totalDiscInformation, 1))

        loomingVbox = QVBoxLayout()
        loomingVbox.addLayout(discForm)
        loomingVbox.addLayout(self.addDiscPushButtonLayout)


        discGroupBox.setLayout(loomingVbox)

        mainvbox.addLayout(loomingFundamentalForm)
        mainvbox.addWidget(discGroupBox)
        mainvbox.addWidget(self.disc_table)
        mainvbox.addLayout(self.deleteDiscPushButtonLayout)
        #mainvbox.setStretch(0,1)
        #mainvbox.setStretch(1,5)


        widget = QWidget()
        widget.setLayout(mainvbox)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(widget)
        scroll_area.setWidgetResizable(True)
        return scroll_area        

    def createGratingTab(self):
        mainvbox = QVBoxLayout()

        gratingGroupBox = QGroupBox('')

        gratingFundamentalForm, gratingForm = self.createGratingTabFormLayout()

        gratingVbox = QVBoxLayout()
        gratingVbox.addLayout(gratingForm)

        gratingGroupBox.setLayout(gratingVbox)

        mainvbox.addLayout(gratingFundamentalForm)
        mainvbox.addWidget(gratingGroupBox)
        #mainvbox.setStretch(0,1)
        #mainvbox.setStretch(1,5)


        widget = QWidget()
        widget.setLayout(mainvbox)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(widget)
        scroll_area.setWidgetResizable(True)
        return scroll_area        


    def createGratingTabFormLayout(self):

        self.grating_vertical_radio_button = QRadioButton("vertical")
        self.grating_horizontal_radio_button = QRadioButton("horizontal")
        self.grating_vertical_radio_button_value = [True]
        self.grating_horizontal_radio_button_value = [False]
        gratingVHRadioButtonLayout = self.createTwoRadioButtonSelectionLayout(self.grating_vertical_radio_button, self.grating_horizontal_radio_button, self.grating_vertical_radio_button_value, self.grating_horizontal_radio_button_value)
        self.grating_vertical_radio_button.clicked.connect(lambda : self.changeGratingRange())
        self.grating_horizontal_radio_button.clicked.connect(lambda : self.changeGratingRange())

        self.grating_square_radio_button = QRadioButton("square")
        self.grating_sine_radio_button = QRadioButton("sine")
        self.grating_square_radio_button_value = [True]
        self.grating_sine_radio_button_value = [False]
        gratingSqSiRadioButtonLayout = self.createTwoRadioButtonSelectionLayout(self.grating_square_radio_button, self.grating_sine_radio_button, self.grating_square_radio_button_value, self.grating_sine_radio_button_value)

        self.grating_position_sigmoid_radio_button = QRadioButton("sigmoid")
        self.grating_position_linear_radio_button = QRadioButton("linear")
        self.grating_position_sigmoid_radio_button_value = [True]
        self.grating_position_linear_radio_button_value = [False]
        gratingSLRadioButtonLayout = self.createTwoRadioButtonSelectionLayout(self.grating_position_sigmoid_radio_button, self.grating_position_linear_radio_button, self.grating_position_sigmoid_radio_button_value, self.grating_position_linear_radio_button_value)

        self.grating_total_pattern_duration_spin_box = QSpinBox()
        self.grating_total_pattern_duration_spin_box.setMinimum(1)
        self.grating_total_pattern_duration_spin_box.setMaximum(DEFAULTMAXIMUMPATTERNLENGTHRANGE)
        self.grating_total_pattern_duration_spin_box.setValue(DEFAULTMAXIMUMPATTERNLENGTH)
        self.grating_total_pattern_duration_spin_box_value = [0]
        self.saveSpinBoxValue(self.grating_total_pattern_duration_spin_box, self.grating_total_pattern_duration_spin_box_value)
        self.grating_total_pattern_duration_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.grating_total_pattern_duration_spin_box, self.grating_total_pattern_duration_spin_box_value))
        self.grating_total_pattern_duration_spin_box.editingFinished.connect(lambda : self.change2MaximumRange(self.grating_movement_start_timing_spin_box, self.grating_total_pattern_duration_spin_box_value[0]))
        self.grating_total_pattern_duration_spin_box.editingFinished.connect(lambda : self.change2MaximumRange(self.grating_movement_end_timing_spin_box, self.grating_total_pattern_duration_spin_box_value[0]))


        self.grating_cycle_length_spin_box = QSpinBox()
        self.grating_cycle_length_spin_box.setMinimum(2)
        self.grating_cycle_length_spin_box.setMaximum(2*DEFAULTDISPLAYERHEIGHT*2)
        self.grating_cycle_length_spin_box.setValue(DEFAULTGRATINGCYCLELENGTH)
        self.grating_cycle_length_spin_box_value = [0]
        self.saveSpinBoxValue(self.grating_cycle_length_spin_box, self.grating_cycle_length_spin_box_value)
        self.grating_cycle_length_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.grating_cycle_length_spin_box, self.grating_cycle_length_spin_box_value))

        self.grating_location_difference_spin_box = QSpinBox()
        #setminimum, minus value should be accepted
        self.grating_location_difference_spin_box.setMinimum(-5*DEFAULTDISPLAYERHEIGHT)
        self.grating_location_difference_spin_box.setMaximum(5*DEFAULTDISPLAYERHEIGHT)
        self.grating_location_difference_spin_box.setValue(DEFAULTGRATINGLOCATIONDIFFERENCE)
        self.grating_location_difference_spin_box_value = [0]
        self.saveSpinBoxValue(self.grating_location_difference_spin_box, self.grating_location_difference_spin_box_value)
        self.grating_location_difference_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.grating_location_difference_spin_box, self.grating_location_difference_spin_box_value))

        self.grating_movement_start_timing_spin_box = QSpinBox()
        self.grating_movement_start_timing_spin_box.setMinimum(1)
        self.grating_movement_start_timing_spin_box.setMaximum(DEFAULTMAXIMUMPATTERNLENGTH)
        self.grating_movement_start_timing_spin_box.setValue(DEFAULTSTARTTIMINGOFTHEMOVEMENT)
        self.grating_movement_start_timing_spin_box_value = [0]
        self.saveSpinBoxValue(self.grating_movement_start_timing_spin_box, self.grating_movement_start_timing_spin_box_value)
        self.grating_movement_start_timing_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.grating_movement_start_timing_spin_box, self.grating_movement_start_timing_spin_box_value))
        self.grating_movement_start_timing_spin_box.editingFinished.connect(lambda: self.change2MinimumValue(self.grating_movement_end_timing_spin_box, self.grating_movement_start_timing_spin_box_value[0]))

        self.grating_movement_end_timing_spin_box = QSpinBox()
        self.grating_movement_end_timing_spin_box.setMinimum(1)
        self.grating_movement_end_timing_spin_box.setMaximum(DEFAULTMAXIMUMPATTERNLENGTH)
        self.grating_movement_end_timing_spin_box.setValue(DEFAULTENDTIMINGOFTHEMOVEMENT)
        self.grating_movement_end_timing_spin_box_value = [0]
        self.saveSpinBoxValue(self.grating_movement_end_timing_spin_box, self.grating_movement_end_timing_spin_box_value)
        self.grating_movement_end_timing_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.grating_movement_end_timing_spin_box, self.grating_movement_end_timing_spin_box_value))
        self.grating_movement_end_timing_spin_box.editingFinished.connect(lambda : self.change2MaximumValue(self.grating_movement_start_timing_spin_box, self.grating_movement_end_timing_spin_box_value[0]))

        self.grating_background_color_push_button = QPushButton('select color')
        self.grating_background_color_frame = QFrame()
        self.grating_background_color = [0, 255, 0]
        gratingBackgroundColorSelectionLayout = self.createColorSelectionLayout(self.grating_background_color_push_button, self.grating_background_color_frame, self.grating_background_color)

        self.grating_color_push_button = QPushButton('select color')
        self.grating_color_frame = QFrame()
        self.grating_color = [0, 0, 0]
        gratingColorSelectionLayout = self.createColorSelectionLayout(self.grating_color_push_button, self.grating_color_frame, self.grating_color)

        gratingFundamentalForm = QFormLayout()
        gratingForm = QFormLayout()

        gratingFundamentalForm.addRow("background color : ", gratingBackgroundColorSelectionLayout)
        gratingFundamentalForm.addRow(" total pattern length(ms) : ", self.grating_total_pattern_duration_spin_box)

        gratingForm.addRow("grating color : ", gratingColorSelectionLayout)
        gratingForm.addRow("cycle length(px) : ", self.grating_cycle_length_spin_box)
        gratingForm.addRow("direction of the grating position : ", gratingVHRadioButtonLayout)
        gratingForm.addRow("function for the grating shape : ", gratingSqSiRadioButtonLayout)
        gratingForm.addRow("function for the grating position : ", gratingSLRadioButtonLayout)
        gratingForm.addRow("grating location difference(px) : ", self.grating_location_difference_spin_box)
        gratingForm.addRow("start timing of the grating movement(ms) : ", self.grating_movement_start_timing_spin_box)
        gratingForm.addRow("end timing of the grating movement(ms) : ", self.grating_movement_end_timing_spin_box)

        return gratingFundamentalForm, gratingForm

    def createFourRadioButtonSelectionLayout(self, radioButton1, radioButton2, radioButton3, radioButton4, radioButtonValue1, radioButtonValue2, radioButtonValue3, radioButtonValue4):
        widget = QWidget(self)
        buttonGroup = QButtonGroup(widget)

        radioButton1.setChecked(True)

        radioButton1.clicked.connect(lambda : self.saveFourRadioButtonValue(radioButton1, radioButtonValue1, radioButtonValue2, radioButtonValue3, radioButtonValue4))
        radioButton2.clicked.connect(lambda : self.saveFourRadioButtonValue(radioButton2, radioButtonValue2, radioButtonValue1, radioButtonValue3, radioButtonValue4))
        radioButton3.clicked.connect(lambda : self.saveFourRadioButtonValue(radioButton3, radioButtonValue3, radioButtonValue1, radioButtonValue2, radioButtonValue4))
        radioButton4.clicked.connect(lambda : self.saveFourRadioButtonValue(radioButton4, radioButtonValue4, radioButtonValue1, radioButtonValue2, radioButtonValue3))

        buttonGroup.addButton(radioButton1)
        buttonGroup.addButton(radioButton2)
        buttonGroup.addButton(radioButton3)
        buttonGroup.addButton(radioButton4)

        RadioButtonLayout = QHBoxLayout()
        RadioButtonLayout.addWidget(radioButton1)
        RadioButtonLayout.addWidget(radioButton2)
        RadioButtonLayout.addWidget(radioButton3)
        RadioButtonLayout.addWidget(radioButton4)

        return RadioButtonLayout


    def saveFourRadioButtonValue(self, turnedOnRadioButton, turnedOnRadioButtonValue, turnedOffRadioButtonValue1, turnedOffRadioButtonValue2, turnedOffRadioButtonValue3):
        turnedOnRadioButtonValue[0] = True
        turnedOffRadioButtonValue1[0] = False
        turnedOffRadioButtonValue2[0] = False
        turnedOffRadioButtonValue3[0] = False

    def createTwoRadioButtonSelectionLayout(self, radioButton1, radioButton2, radioButtonValue1, radioButtonValue2):
        widget = QWidget(self)
        buttonGroup = QButtonGroup(widget)

        radioButton1.setChecked(True)

        radioButton1.clicked.connect(lambda : self.saveTwoRadioButtonValue(radioButton1, radioButtonValue1, radioButtonValue2))
        radioButton2.clicked.connect(lambda : self.saveTwoRadioButtonValue(radioButton2, radioButtonValue2, radioButtonValue1))

        buttonGroup.addButton(radioButton1)
        buttonGroup.addButton(radioButton2)

        RadioButtonLayout = QHBoxLayout()
        RadioButtonLayout.addWidget(radioButton1)
        RadioButtonLayout.addWidget(radioButton2)
        
        return RadioButtonLayout

    def saveTwoRadioButtonValue(self, turnedOnRadioButton, turnedOnRadioButtonValue, turnedOffRadioButtonValue):
        turnedOnRadioButtonValue[0] = True
        turnedOffRadioButtonValue[0] = False



    def deleteRowData(self, checkBoxList, currentobjectCnt, checkBoxValueList, table, totalInformationList, objectNumberRowIndex):
        
        for i in range(currentobjectCnt[0]):
            if checkBoxList[i].isChecked():
                checkBoxValueList.append(1)
            else:
                checkBoxValueList.append(0)
        
        for i, value in reversed(list(enumerate(checkBoxValueList))):

            if(value):
                table.removeRow(i+1)
                currentobjectCnt[0] -= 1

                totalInformationList.pop(i)
                checkBoxList.pop(i)

        checkBoxValueList.clear()
        
        for i in range(currentobjectCnt[0]):
            totalInformationList[i][0] = i+1
            table.setItem(i+1, objectNumberRowIndex, QTableWidgetItem(str(i+1)))
            table.item(i+1, objectNumberRowIndex).setTextAlignment(Qt.AlignCenter)



    def saveNAddData(self, objectType, currentObjectCnt, totalInformation, table, checkBoxList):
        currentObjectCnt[0] += 1

        if(objectType == "Bar"):
            func = self.getCurrentBarData()
        elif(objectType == "Spot"):
            func = self.getCurrentSpotData()
        elif(objectType == "Disc"):
            func = self.getCurrentDiscData()
        totalInformation.append(func)

        self.insertRowNValueInTable(currentObjectCnt[0], totalInformation, table, checkBoxList)
        #print(totalInformation)

    def insertRowNValueInTable(self, objectCnt, InformationArr, table, checkBoxList):
        table.insertRow(objectCnt)

        ckbox = QCheckBox()
        checkBoxList.append(ckbox)

        layoutCB = QHBoxLayout()
        layoutCB.addWidget(checkBoxList[objectCnt-1])
        layoutCB.setAlignment(Qt.AlignCenter)            
        layoutCB.setContentsMargins(0,0,0,0)

        cellWidget = QWidget()
        cellWidget.setLayout(layoutCB)

        table.setCellWidget(objectCnt, 0, cellWidget)            

        for i in range(len(InformationArr[objectCnt-1])):
            table.setItem(objectCnt, i+1, QTableWidgetItem(str(InformationArr[objectCnt-1][i])))
            
            if(type(InformationArr[objectCnt-1][i]) is list):
                color_RGB = np.array(InformationArr[objectCnt-1][i])
                table.item(objectCnt,i+1).setBackground(QColor(*color_RGB))
                table.item(objectCnt,i+1).setForeground(QColor(*(np.array([255,255,255])-color_RGB)))

            table.item(objectCnt,i+1).setTextAlignment(Qt.AlignCenter)

    def getCurrentBarData(self):
            dir_of_the_bar_pos = "vertical" if self.bar_vertical_radio_button_value[0] == True else "horizontal"
            func_for_the_bar_pos = "sigmoid" if self.bar_position_sigmoid_radio_button_value[0] == True else "linear"

            barData = [self.currentBarCnt[0],self.bar_color.copy(),self.bar_width_spin_box_value[0], dir_of_the_bar_pos, self.initial_bar_location_spin_box_value[0], self.final_bar_location_spin_box_value[0], func_for_the_bar_pos, self.bar_movement_start_timing_spin_box_value[0], self.bar_movement_end_timing_spin_box_value[0]]
            return barData

    def getCurrentSpotData(self):
            dir_of_the_spot_pos = "vertical" if self.spot_vertical_radio_button_value[0] == True else "horizontal"
            func_for_the_spot_pos = "sigmoid" if self.spot_position_sigmoid_radio_button_value[0] == True else "linear"
            
            spotData = [self.currentSpotCnt[0],self.spot_color.copy(),self.spot_width_spin_box_value[0],self.spot_height_spin_box_value[0],dir_of_the_spot_pos,self.initial_spot_x_location_spin_box_value[0],self.initial_spot_y_location_spin_box_value[0],self.final_spot_x_location_spin_box_value[0],self.final_spot_y_location_spin_box_value[0],func_for_the_spot_pos, self.spot_movement_start_timing_spin_box_value[0], self.spot_movement_end_timing_spin_box_value[0]]
            return spotData

    def getCurrentDiscData(self):
            discData = [self.currentDiscCnt[0],self.disc_color.copy(),self.disc_x_location_spin_box_value[0],self.disc_y_location_spin_box_value[0],self.initial_disc_radius_spin_box_value[0],self.final_disc_radius_spin_box_value[0],self.looming_movement_start_timing_spin_box_value[0],self.looming_movement_end_timing_spin_box_value[0]]
            return discData


    def change2MaximumRange(self,spinbox, maximum):
        spinbox.setMaximum(maximum)

    def change2MaximumValue(self, spinbox, maximum):
        if spinbox.value() > maximum:
            spinbox.setValue(maximum)

    def change2MinimumValue(self, spinbox, minimum):
        if spinbox.value() < minimum:
            spinbox.setValue(minimum)


    def changeBarRange(self):
        maximumValue = 0
        if(self.bar_vertical_radio_button_value[0] == True):
            maximumValue = self.displayer_height_value[0]
        else:
            maximumValue = self.displayer_width_value[0]
        
        self.bar_width_spin_box.setMaximum(maximumValue)
        self.initial_bar_location_spin_box.setMaximum(maximumValue)
        self.final_bar_location_spin_box.setMaximum(maximumValue)

    def changeSpotWidthRange(self):
        self.spot_width_spin_box.setMaximum(self.displayer_width_value[0])
        self.initial_spot_x_location_spin_box.setMaximum(self.displayer_width_value[0])
        self.final_spot_x_location_spin_box.setMaximum(self.displayer_width_value[0])

    def changeSpotHeightRange(self):
        self.spot_height_spin_box.setMaximum(self.displayer_height_value[0])
        self.initial_spot_y_location_spin_box.setMaximum(self.displayer_height_value[0])
        self.final_spot_y_location_spin_box.setMaximum(self.displayer_height_value[0])

    def changeGratingRange(self):
        maximumValue = 0
        if(self.grating_vertical_radio_button_value[0] == True):
            maximumValue = self.displayer_height_value[0]
        else:
            maximumValue = self.displayer_width_value[0]
        
        self.grating_cycle_length_spin_box.setMaximum(2*maximumValue)
        self.grating_location_difference_spin_box.setMinimum(-5*maximumValue)
        self.grating_location_difference_spin_box.setMaximum(5*maximumValue)


    def createBarTabFormLayout(self):

        self.bar_vertical_radio_button = QRadioButton("vertical")
        self.bar_horizontal_radio_button = QRadioButton("horizontal")
        self.bar_vertical_radio_button_value = [True]
        self.bar_horizontal_radio_button_value = [False]
        barVHRadioButtonLayout = self.createTwoRadioButtonSelectionLayout(self.bar_vertical_radio_button, self.bar_horizontal_radio_button, self.bar_vertical_radio_button_value, self.bar_horizontal_radio_button_value)
        self.bar_vertical_radio_button.clicked.connect(lambda : self.changeBarRange())
        self.bar_horizontal_radio_button.clicked.connect(lambda : self.changeBarRange())

        self.bar_position_sigmoid_radio_button = QRadioButton("sigmoid")
        self.bar_position_linear_radio_button = QRadioButton("linear")
        self.bar_position_sigmoid_radio_button_value = [True]
        self.bar_position_linear_radio_button_value = [False]
        barSLRadioButtonLayout = self.createTwoRadioButtonSelectionLayout(self.bar_position_sigmoid_radio_button, self.bar_position_linear_radio_button, self.bar_position_sigmoid_radio_button_value, self.bar_position_linear_radio_button_value)


        self.bar_total_pattern_duration_spin_box = QSpinBox()
        self.bar_total_pattern_duration_spin_box.setMinimum(1)
        self.bar_total_pattern_duration_spin_box.setMaximum(DEFAULTMAXIMUMPATTERNLENGTHRANGE)
        self.bar_total_pattern_duration_spin_box.setValue(DEFAULTMAXIMUMPATTERNLENGTH)
        self.bar_total_pattern_duration_spin_box_value =[0]
        self.saveSpinBoxValue(self.bar_total_pattern_duration_spin_box, self.bar_total_pattern_duration_spin_box_value)
        self.bar_total_pattern_duration_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.bar_total_pattern_duration_spin_box, self.bar_total_pattern_duration_spin_box_value))
        self.bar_total_pattern_duration_spin_box.editingFinished.connect(lambda : self.change2MaximumRange(self.bar_movement_start_timing_spin_box, self.bar_total_pattern_duration_spin_box_value[0]))
        self.bar_total_pattern_duration_spin_box.editingFinished.connect(lambda : self.change2MaximumRange(self.bar_movement_end_timing_spin_box,self.bar_total_pattern_duration_spin_box_value[0]))

        self.initial_bar_location_spin_box = QSpinBox()
        self.initial_bar_location_spin_box.setMinimum(-DEFAULTDISPLAYERHEIGHT)
        self.initial_bar_location_spin_box.setMaximum(2*DEFAULTDISPLAYERHEIGHT)
        self.initial_bar_location_spin_box.setValue(DEFAULTINITIALBARMIDPOINTPOSITION)
        self.initial_bar_location_spin_box_value = [0]
        self.saveSpinBoxValue(self.initial_bar_location_spin_box, self.initial_bar_location_spin_box_value)
        self.initial_bar_location_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.initial_bar_location_spin_box, self.initial_bar_location_spin_box_value))

        self.final_bar_location_spin_box = QSpinBox()
        self.final_bar_location_spin_box.setMinimum(-DEFAULTDISPLAYERHEIGHT)
        self.final_bar_location_spin_box.setMaximum(2*DEFAULTDISPLAYERHEIGHT)
        self.final_bar_location_spin_box.setValue(DEFAULTFINALBARMIDPOINTPOSITION)
        self.final_bar_location_spin_box_value = [0]
        self.saveSpinBoxValue(self.final_bar_location_spin_box, self.final_bar_location_spin_box_value)
        self.final_bar_location_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.final_bar_location_spin_box, self.final_bar_location_spin_box_value))

        self.bar_width_spin_box = QSpinBox()
        #self.changeBarRange()
        self.bar_width_spin_box.setMinimum(1)
        self.bar_width_spin_box.setMaximum(DEFAULTDISPLAYERHEIGHT)
        self.bar_width_spin_box.setValue(DEFAULTBARWIDTH)
        self.bar_width_spin_box_value = [0]
        self.saveSpinBoxValue(self.bar_width_spin_box, self.bar_width_spin_box_value)
        self.bar_width_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.bar_width_spin_box, self.bar_width_spin_box_value))

        self.bar_movement_start_timing_spin_box = QSpinBox()
        self.bar_movement_start_timing_spin_box.setMinimum(1)
        self.bar_movement_start_timing_spin_box.setMaximum(DEFAULTMAXIMUMPATTERNLENGTH)
        self.bar_movement_start_timing_spin_box.setValue(DEFAULTSTARTTIMINGOFTHEMOVEMENT)
        self.bar_movement_start_timing_spin_box_value = [0]
        self.saveSpinBoxValue(self.bar_movement_start_timing_spin_box, self.bar_movement_start_timing_spin_box_value)
        self.bar_movement_start_timing_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.bar_movement_start_timing_spin_box, self.bar_movement_start_timing_spin_box_value))
        self.bar_movement_start_timing_spin_box.editingFinished.connect(lambda: self.change2MinimumValue(self.bar_movement_end_timing_spin_box, self.bar_movement_start_timing_spin_box_value[0]))

        self.bar_movement_end_timing_spin_box = QSpinBox()
        self.bar_movement_end_timing_spin_box.setMinimum(1)
        self.bar_movement_end_timing_spin_box.setMaximum(DEFAULTMAXIMUMPATTERNLENGTH)
        self.bar_movement_end_timing_spin_box.setValue(DEFAULTENDTIMINGOFTHEMOVEMENT)
        self.bar_movement_end_timing_spin_box_value = [0]
        self.saveSpinBoxValue(self.bar_movement_end_timing_spin_box, self.bar_movement_end_timing_spin_box_value)
        self.bar_movement_end_timing_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.bar_movement_end_timing_spin_box, self.bar_movement_end_timing_spin_box_value))
        self.bar_movement_end_timing_spin_box.editingFinished.connect(lambda : self.change2MaximumValue(self.bar_movement_start_timing_spin_box, self.bar_movement_end_timing_spin_box_value[0]))

        self.bar_background_color_push_button = QPushButton('select color')
        self.bar_background_color_frame = QFrame()
        self.bar_background_color = [0, 255, 0]
        barBackgroundColorSelectionLayout = self.createColorSelectionLayout(self.bar_background_color_push_button, self.bar_background_color_frame, self.bar_background_color)

        self.bar_color_push_button = QPushButton('select color')
        self.bar_color_frame = QFrame()
        self.bar_color = [0, 0, 0]
        barColorSelectionLayout = self.createColorSelectionLayout(self.bar_color_push_button, self.bar_color_frame, self.bar_color)

        barFundamentalForm = QFormLayout()
        barForm = QFormLayout()

        barFundamentalForm.addRow(" background color : ", barBackgroundColorSelectionLayout)
        barFundamentalForm.addRow(" total pattern length(ms) : ", self.bar_total_pattern_duration_spin_box)

        barForm.addRow("bar color : ", barColorSelectionLayout)
        barForm.addRow("bar width(px) : ", self.bar_width_spin_box)
        barForm.addRow("direction of the bar position : ", barVHRadioButtonLayout)
        barForm.addRow("initial bar midpoint position(px) : ", self.initial_bar_location_spin_box)
        barForm.addRow("final bar midpoint position(px) : ", self.final_bar_location_spin_box)
        barForm.addRow("function for the bar position : ", barSLRadioButtonLayout)
        barForm.addRow("start timing of the bar movement(ms) : ", self.bar_movement_start_timing_spin_box)
        barForm.addRow("end timing of the bar movement(ms) : ", self.bar_movement_end_timing_spin_box)

        return barFundamentalForm, barForm

    def createColorSelectionLayout(self, colorSelectionPushButton, colorFrame, colorRGBValue):

        hbox = QHBoxLayout()

        col = QColor(*colorRGBValue)
        colorSelectionPushButton.clicked.connect(lambda : self.showColorDialog(colorFrame,colorRGBValue))
        colorFrame.setStyleSheet('QWidget { background-color: %s }' % col.name())

        hbox.addWidget(colorSelectionPushButton)
        hbox.addWidget(colorFrame)

        return hbox

    def disableNEnableSpinboxes(self,spinBoxToDisable,spinBoxToEnable,spinBoxToGetValue):
        spinBoxToDisable.setDisabled(True)
        spinBoxToEnable.setEnabled(True)
        spinBoxToDisable.setValue(spinBoxToGetValue.value())

    def connectTwoSpinBoxValueIfDisabled(self,disabledSpinBox,enableSpinBox):
        if(not(disabledSpinBox.isEnabled())):
            disabledSpinBox.setValue(enableSpinBox.value())


    def createSpotTabFormLayout(self):

        self.spot_vertical_radio_button = QRadioButton("vertical")
        self.spot_horizontal_radio_button = QRadioButton("horizontal")
        self.spot_vertical_radio_button_value = [True]
        self.spot_horizontal_radio_button_value = [False]
        spotVHRadioButtonLayout = self.createTwoRadioButtonSelectionLayout(self.spot_vertical_radio_button, self.spot_horizontal_radio_button, self.spot_vertical_radio_button_value, self.spot_horizontal_radio_button_value)
        self.spot_vertical_radio_button.clicked.connect(lambda : self.disableNEnableSpinboxes(self.final_spot_x_location_spin_box, self.final_spot_y_location_spin_box, self.initial_spot_x_location_spin_box))
        self.spot_horizontal_radio_button.clicked.connect(lambda : self.disableNEnableSpinboxes(self.final_spot_y_location_spin_box, self.final_spot_x_location_spin_box, self.initial_spot_y_location_spin_box))

        self.spot_position_sigmoid_radio_button = QRadioButton("sigmoid")
        self.spot_position_linear_radio_button = QRadioButton("linear")
        self.spot_position_sigmoid_radio_button_value = [True]
        self.spot_position_linear_radio_button_value = [False]
        spotSLRadioButtonLayout = self.createTwoRadioButtonSelectionLayout(self.spot_position_sigmoid_radio_button, self.spot_position_linear_radio_button, self.spot_position_sigmoid_radio_button_value, self.spot_position_linear_radio_button_value)


        self.spot_total_pattern_duration_spin_box = QSpinBox()
        self.spot_total_pattern_duration_spin_box.setMinimum(1)
        self.spot_total_pattern_duration_spin_box.setMaximum(DEFAULTMAXIMUMPATTERNLENGTHRANGE)
        self.spot_total_pattern_duration_spin_box.setValue(DEFAULTMAXIMUMPATTERNLENGTH)
        self.spot_total_pattern_duration_spin_box_value =[0]
        self.saveSpinBoxValue(self.spot_total_pattern_duration_spin_box, self.spot_total_pattern_duration_spin_box_value)
        self.spot_total_pattern_duration_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.spot_total_pattern_duration_spin_box, self.spot_total_pattern_duration_spin_box_value))
        self.spot_total_pattern_duration_spin_box.editingFinished.connect(lambda: self.change2MaximumRange(self.spot_movement_start_timing_spin_box, self.spot_total_pattern_duration_spin_box_value[0]))
        self.spot_total_pattern_duration_spin_box.editingFinished.connect(lambda : self.change2MaximumRange(self.spot_movement_end_timing_spin_box, self.spot_total_pattern_duration_spin_box_value[0]))


        self.spot_width_spin_box = QSpinBox()
        self.spot_width_spin_box.setMinimum(1)
        self.spot_width_spin_box.setMaximum(DEFAULTDISPLAYERWIDTH)
        self.spot_width_spin_box.setValue(DEFAULTSPOTWIDTH)
        self.spot_width_spin_box_value =[0]
        self.saveSpinBoxValue(self.spot_width_spin_box, self.spot_width_spin_box_value)
        self.spot_width_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.spot_width_spin_box, self.spot_width_spin_box_value))

        self.spot_height_spin_box = QSpinBox()
        self.spot_height_spin_box.setMinimum(1)
        self.spot_height_spin_box.setMaximum(DEFAULTDISPLAYERHEIGHT)
        self.spot_height_spin_box.setValue(DEFAULTSPOTHEIGHT)
        self.spot_height_spin_box_value =[0]
        self.saveSpinBoxValue(self.spot_height_spin_box, self.spot_height_spin_box_value)
        self.spot_height_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.spot_height_spin_box, self.spot_height_spin_box_value))

        self.initial_spot_x_location_spin_box = QSpinBox()
        self.initial_spot_x_location_spin_box.setMinimum(-DEFAULTDISPLAYERWIDTH)
        self.initial_spot_x_location_spin_box.setMaximum(2*DEFAULTDISPLAYERWIDTH)
        self.initial_spot_x_location_spin_box.setValue(DEFAULTINITIALSPOTMIDPOINTXPOSITION)
        self.initial_spot_x_location_spin_box_value =[0]
        self.saveSpinBoxValue(self.initial_spot_x_location_spin_box, self.initial_spot_x_location_spin_box_value)
        self.initial_spot_x_location_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.initial_spot_x_location_spin_box, self.initial_spot_x_location_spin_box_value))
        self.initial_spot_x_location_spin_box.editingFinished.connect(lambda : self.connectTwoSpinBoxValueIfDisabled(self.final_spot_x_location_spin_box, self.initial_spot_x_location_spin_box))
        
        self.initial_spot_y_location_spin_box = QSpinBox()
        self.initial_spot_y_location_spin_box.setMinimum(-DEFAULTDISPLAYERHEIGHT)
        self.initial_spot_y_location_spin_box.setMaximum(2*DEFAULTDISPLAYERHEIGHT)
        self.initial_spot_y_location_spin_box.setValue(DEFAULTINITIALSPOTMIDPOINTYPOSITION)
        self.initial_spot_y_location_spin_box_value =[0]
        self.saveSpinBoxValue(self.initial_spot_y_location_spin_box, self.initial_spot_y_location_spin_box_value)
        self.initial_spot_y_location_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.initial_spot_y_location_spin_box, self.initial_spot_y_location_spin_box_value))
        self.initial_spot_y_location_spin_box.editingFinished.connect(lambda : self.connectTwoSpinBoxValueIfDisabled(self.final_spot_y_location_spin_box, self.initial_spot_y_location_spin_box))

        self.final_spot_x_location_spin_box = QSpinBox()
        self.final_spot_x_location_spin_box.setMinimum(-DEFAULTDISPLAYERWIDTH)
        self.final_spot_x_location_spin_box.setMaximum(2*DEFAULTDISPLAYERWIDTH)
        self.final_spot_x_location_spin_box.setValue(DEFAULTFINALSPOTMIDPOINTXPOSITION)
        self.final_spot_x_location_spin_box_value =[0]
        self.saveSpinBoxValue(self.final_spot_x_location_spin_box, self.final_spot_x_location_spin_box_value)
        self.final_spot_x_location_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.final_spot_x_location_spin_box, self.final_spot_x_location_spin_box_value))
        self.final_spot_x_location_spin_box.setDisabled(True)


        self.final_spot_y_location_spin_box = QSpinBox()
        self.final_spot_y_location_spin_box.setMinimum(-DEFAULTDISPLAYERHEIGHT)
        self.final_spot_y_location_spin_box.setMaximum(2*DEFAULTDISPLAYERHEIGHT)
        self.final_spot_y_location_spin_box.setValue(DEFAULTFINALSPOTMIDPOINTYPOSITION)
        self.final_spot_y_location_spin_box_value =[0]
        self.saveSpinBoxValue(self.final_spot_y_location_spin_box, self.final_spot_y_location_spin_box_value)
        self.final_spot_y_location_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.final_spot_y_location_spin_box, self.final_spot_y_location_spin_box_value))

        self.spot_movement_start_timing_spin_box = QSpinBox()
        self.spot_movement_start_timing_spin_box.setMinimum(1)
        self.spot_movement_start_timing_spin_box.setMaximum(DEFAULTMAXIMUMPATTERNLENGTH)
        self.spot_movement_start_timing_spin_box.setValue(DEFAULTSTARTTIMINGOFTHEMOVEMENT)
        self.spot_movement_start_timing_spin_box_value = [0]
        self.saveSpinBoxValue(self.spot_movement_start_timing_spin_box, self.spot_movement_start_timing_spin_box_value)
        self.spot_movement_start_timing_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.spot_movement_start_timing_spin_box, self.spot_movement_start_timing_spin_box_value))
        self.spot_movement_start_timing_spin_box.editingFinished.connect(lambda: self.change2MinimumValue(self.spot_movement_end_timing_spin_box, self.spot_movement_start_timing_spin_box_value[0]))
        
        self.spot_movement_end_timing_spin_box = QSpinBox()
        self.spot_movement_end_timing_spin_box.setMinimum(1)
        self.spot_movement_end_timing_spin_box.setMaximum(DEFAULTMAXIMUMPATTERNLENGTH)
        self.spot_movement_end_timing_spin_box.setValue(DEFAULTENDTIMINGOFTHEMOVEMENT)
        self.spot_movement_end_timing_spin_box_value =[0]
        self.saveSpinBoxValue(self.spot_movement_end_timing_spin_box, self.spot_movement_end_timing_spin_box_value)
        self.spot_movement_end_timing_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.spot_movement_end_timing_spin_box, self.spot_movement_end_timing_spin_box_value))
        self.spot_movement_end_timing_spin_box.editingFinished.connect(lambda : self.change2MaximumValue(self.spot_movement_start_timing_spin_box, self.spot_movement_end_timing_spin_box_value[0]))

        self.spot_background_color_push_button = QPushButton('select color')
        self.spot_background_color_frame = QFrame()
        self.spot_background_color = [0, 255, 0]
        spotBackgroundColorSelectionLayout = self.createColorSelectionLayout(self.spot_background_color_push_button, self.spot_background_color_frame, self.spot_background_color)

        self.spot_color_push_button = QPushButton('select color')
        self.spot_color_frame = QFrame()
        self.spot_color = [0, 0, 0]
        spotColorSelectionLayout = self.createColorSelectionLayout(self.spot_color_push_button, self.spot_color_frame, self.spot_color)

        spotFundamentalForm = QFormLayout()
        spotForm = QFormLayout()
        
        spotFundamentalForm.addRow(" background color : ", spotBackgroundColorSelectionLayout)
        spotFundamentalForm.addRow(" total pattern length(ms) : ", self.spot_total_pattern_duration_spin_box)

        spotForm.addRow("spot color : ", spotColorSelectionLayout)
        spotForm.addRow("spot width(px) : ", self.spot_width_spin_box)
        spotForm.addRow("spot height(px) : ", self.spot_height_spin_box)
        spotForm.addRow("direction of the spot position : ", spotVHRadioButtonLayout)
        spotForm.addRow("initial spot midpoint x position(px) : ", self.initial_spot_x_location_spin_box)
        spotForm.addRow("initial spot midpoint y position(px) : ", self.initial_spot_y_location_spin_box)
        spotForm.addRow("final spot midpoint x position(px) : ", self.final_spot_x_location_spin_box)
        spotForm.addRow("final spot midpoint y position(px) : ", self.final_spot_y_location_spin_box)
        spotForm.addRow("function for the spot position : ", spotSLRadioButtonLayout)
        spotForm.addRow("start timing of the spot movement(ms) : ", self.spot_movement_start_timing_spin_box)
        spotForm.addRow("end timing of the spot movement(ms) : ", self.spot_movement_end_timing_spin_box)

        return spotFundamentalForm, spotForm




    def createLoomingTabFormLayout(self):
        
        self.looming_total_pattern_duration_spin_box = QSpinBox()
        self.looming_total_pattern_duration_spin_box.setMinimum(1)
        self.looming_total_pattern_duration_spin_box.setMaximum(DEFAULTMAXIMUMPATTERNLENGTHRANGE)
        self.looming_total_pattern_duration_spin_box.setValue(DEFAULTMAXIMUMPATTERNLENGTH)
        self.looming_total_pattern_duration_spin_box_value = [0]
        self.saveSpinBoxValue(self.looming_total_pattern_duration_spin_box, self.looming_total_pattern_duration_spin_box_value)
        self.looming_total_pattern_duration_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.looming_total_pattern_duration_spin_box, self.looming_total_pattern_duration_spin_box_value))
        self.looming_total_pattern_duration_spin_box.editingFinished.connect(lambda: self.change2MaximumRange(self.looming_movement_start_timing_spin_box, self.looming_total_pattern_duration_spin_box_value[0]))
        self.looming_total_pattern_duration_spin_box.editingFinished.connect(lambda : self.change2MaximumRange(self.looming_movement_end_timing_spin_box, self.looming_total_pattern_duration_spin_box_value[0]))


        self.looming_display_covering_angle_spin_box = QDoubleSpinBox()
        self.looming_display_covering_angle_spin_box.setMinimum(1)
        self.looming_display_covering_angle_spin_box.setMaximum(360)
        self.looming_display_covering_angle_spin_box.setValue(DEFAULTDISPLAYCOVERINGANGLE)
        self.looming_display_covering_angle_spin_box.setDecimals(1)
        self.looming_display_covering_angle_spin_box.setSingleStep(0.1)
        self.looming_display_covering_angle_spin_box_value = [0]
        self.saveSpinBoxValue(self.looming_display_covering_angle_spin_box, self.looming_display_covering_angle_spin_box_value)
        self.looming_display_covering_angle_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.looming_display_covering_angle_spin_box, self.looming_display_covering_angle_spin_box_value))
        self.looming_display_covering_angle_spin_box.editingFinished.connect(lambda: self.change2MaximumRange(self.initial_disc_radius_spin_box, self.looming_display_covering_angle_spin_box_value[0]))
        self.looming_display_covering_angle_spin_box.editingFinished.connect(lambda: self.change2MaximumRange(self.final_disc_radius_spin_box, self.looming_display_covering_angle_spin_box_value[0]))


        self.disc_x_location_spin_box = QSpinBox()
        self.disc_x_location_spin_box.setMinimum(-DEFAULTDISPLAYERWIDTH)
        self.disc_x_location_spin_box.setMaximum(2*DEFAULTDISPLAYERWIDTH)
        self.disc_x_location_spin_box.setValue(DEFAULTINITIALLOOMINGMIDPOINTXPOSITION)
        self.disc_x_location_spin_box_value = [0]
        self.saveSpinBoxValue(self.disc_x_location_spin_box, self.disc_x_location_spin_box_value)
        self.disc_x_location_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.disc_x_location_spin_box, self.disc_x_location_spin_box_value))

        self.disc_y_location_spin_box = QSpinBox()
        self.disc_y_location_spin_box.setMinimum(-DEFAULTDISPLAYERHEIGHT)
        self.disc_y_location_spin_box.setMaximum(2*DEFAULTDISPLAYERHEIGHT)
        self.disc_y_location_spin_box.setValue(DEFAULTINITIALLOOMINGMIDPOINTYPOSITION)
        self.disc_y_location_spin_box_value = [0]
        self.saveSpinBoxValue(self.disc_y_location_spin_box, self.disc_y_location_spin_box_value)
        self.disc_y_location_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.disc_y_location_spin_box, self.disc_y_location_spin_box_value))

        self.initial_disc_radius_spin_box = QDoubleSpinBox()
        self.initial_disc_radius_spin_box.setMinimum(0.1)
        self.initial_disc_radius_spin_box.setMaximum(2*DEFAULTDISPLAYCOVERINGANGLE)
        self.initial_disc_radius_spin_box.setValue(DEFAULTINITIALDISCRADIUS)
        self.initial_disc_radius_spin_box.setDecimals(1)
        self.initial_disc_radius_spin_box.setSingleStep(0.1)
        self.initial_disc_radius_spin_box_value = [0]
        self.saveSpinBoxValue(self.initial_disc_radius_spin_box, self.initial_disc_radius_spin_box_value)
        self.initial_disc_radius_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.initial_disc_radius_spin_box, self.initial_disc_radius_spin_box_value))
        self.initial_disc_radius_spin_box.editingFinished.connect(lambda: self.change2MinimumValue(self.final_disc_radius_spin_box, self.initial_disc_radius_spin_box_value[0]))


        self.final_disc_radius_spin_box = QDoubleSpinBox()
        self.final_disc_radius_spin_box.setMinimum(0.1)
        self.final_disc_radius_spin_box.setMaximum(2*DEFAULTDISPLAYCOVERINGANGLE)
        self.final_disc_radius_spin_box.setValue(DEFAULTFINALDISCRADIUS)
        self.final_disc_radius_spin_box.setDecimals(1)
        self.final_disc_radius_spin_box.setSingleStep(0.1)
        self.final_disc_radius_spin_box_value = [0]
        self.saveSpinBoxValue(self.final_disc_radius_spin_box, self.final_disc_radius_spin_box_value)
        self.final_disc_radius_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.final_disc_radius_spin_box, self.final_disc_radius_spin_box_value))
        self.final_disc_radius_spin_box.editingFinished.connect(lambda: self.change2MaximumValue(self.initial_disc_radius_spin_box, self.final_disc_radius_spin_box_value[0]))



        self.looming_movement_start_timing_spin_box = QSpinBox()
        self.looming_movement_start_timing_spin_box.setMinimum(1)
        self.looming_movement_start_timing_spin_box.setMaximum(DEFAULTMAXIMUMPATTERNLENGTH)
        self.looming_movement_start_timing_spin_box.setValue(DEFAULTSTARTTIMINGOFTHEMOVEMENT)
        self.looming_movement_start_timing_spin_box_value = [0]
        self.saveSpinBoxValue(self.looming_movement_start_timing_spin_box, self.looming_movement_start_timing_spin_box_value)
        self.looming_movement_start_timing_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.looming_movement_start_timing_spin_box, self.looming_movement_start_timing_spin_box_value))
        self.looming_movement_start_timing_spin_box.editingFinished.connect(lambda: self.change2MinimumValue(self.looming_movement_end_timing_spin_box, self.looming_movement_start_timing_spin_box_value[0]))

        self.looming_movement_end_timing_spin_box = QSpinBox()
        self.looming_movement_end_timing_spin_box.setMinimum(1)
        self.looming_movement_end_timing_spin_box.setMaximum(DEFAULTMAXIMUMPATTERNLENGTH)
        self.looming_movement_end_timing_spin_box.setValue(DEFAULTENDTIMINGOFTHEMOVEMENT)
        self.looming_movement_end_timing_spin_box_value = [0]
        self.saveSpinBoxValue(self.looming_movement_end_timing_spin_box, self.looming_movement_end_timing_spin_box_value)
        self.looming_movement_end_timing_spin_box.valueChanged.connect(lambda : self.saveSpinBoxValue(self.looming_movement_end_timing_spin_box, self.looming_movement_end_timing_spin_box_value))
        self.looming_movement_end_timing_spin_box.editingFinished.connect(lambda : self.change2MaximumValue(self.looming_movement_start_timing_spin_box, self.looming_movement_end_timing_spin_box_value[0]))

        self.looming_background_color_push_button = QPushButton('select color')
        self.looming_background_color_frame = QFrame()
        self.looming_background_color = [0, 255, 0]
        loomingBackgroundColorSelectionLayout = self.createColorSelectionLayout(self.looming_background_color_push_button, self.looming_background_color_frame, self.looming_background_color)

        self.disc_color_push_button = QPushButton('select color')
        self.disc_color_frame = QFrame()
        self.disc_color = [0, 0, 0]
        discColorSelectionLayout = self.createColorSelectionLayout(self.disc_color_push_button, self.disc_color_frame, self.disc_color)

        loomingFundamentalForm = QFormLayout()
        discForm = QFormLayout()

        loomingFundamentalForm.addRow("background color : ", loomingBackgroundColorSelectionLayout)
        loomingFundamentalForm.addRow(" total pattern length(ms) : ", self.looming_total_pattern_duration_spin_box)
        loomingFundamentalForm.addRow(" display covering angle(°) : ", self.looming_display_covering_angle_spin_box)

        discForm.addRow("disc color : ", discColorSelectionLayout)
        discForm.addRow("disc x location(px) : ", self.disc_x_location_spin_box)
        discForm.addRow("disc y location(px) : ", self.disc_y_location_spin_box)
        discForm.addRow("initial disc radius(°) : ", self.initial_disc_radius_spin_box)
        discForm.addRow("final disc radius(°) : ", self.final_disc_radius_spin_box)
        discForm.addRow("start timing of the disc movement(ms) : ", self.looming_movement_start_timing_spin_box)
        discForm.addRow("end timing of the disc movement(ms) : ", self.looming_movement_end_timing_spin_box)

        return loomingFundamentalForm, discForm


    def showColorDialog(self,color_frame,colorRGBValue):
        col = QColorDialog.getColor()

        if col.isValid():
            color_frame.setStyleSheet('QWidget { background-color: %s }' % col.name())
            colorRGBValue[:] = [col.red(),col.green(),col.blue()]
        else:
            col = QColor(*colorRGBValue)
        
        color_frame.setStyleSheet('QWidget { background-color: %s }' % col.name())


    def saveSpinBoxValue(self, spinBox, spinBoxValue):
        #print('save : ' + str(spinBox.value()))
        #print('max : ' + str(spinBox.maximum()))
        #print('min : ' + str(spinBox.minimum()))
        spinBoxValue[0] = spinBox.value()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    patternGenerator = MyApp()
    patternGenerator.show()
    sys.exit(app.exec_())


