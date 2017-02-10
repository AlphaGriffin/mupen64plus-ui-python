# -*- coding: utf-8 -*-
# Author: Ruckusist @ AlphaGriffin <Alphagriffin.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from m64py.frontend.agblank import AGBlank
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import pyqtSlot, QTimer
import os, sys, pygame, time, shutil
from glob import glob as check
import pandas as pd
VERSION = sys.version

# FIXME
INTRO =\
"""
TRAINING AND CONVERSION SOFTWARE:
        Select from multiple saves of a single game to create a dataset. This
        dataset will need to be converted to a proper image size and coloring.
        Then the dataset needs to be split into training, testing and 
        validation sets. From there a model can be created with the use of a 
        single opimization pass with random settings to create and save your 
        model. At this point you can take your model and optimization function
        to AWS and pay the 5 cents to run your model for an hour or 2. Ill need
        to add instructions for that. Unless you have sufficent graphics card
        to try and train it on your machine.
        
        Step one. Pick multiple files from a single game.
        Step Two. Batch Convert images and create a running numpy object(3d) of
        2d arrays. Save That and the controller input(label) as Input:label for
        your dataset.
        Step Three. Split the dataset into 3 different single object python
        dictionaries, which are Input:label for Train, test, and verifcation.
        Step Four. Verify the shit out of previous steps and create and save a
        model with a single optimization.
        Step Five. Training a dataset is a matter of running through every
        image in the training set and optimizing the necessary weights and
        balances for the model to correctly give a label to an image.
""".format(VERSION,)


# FIXME ADD NOTATION FOR THIS
class xpad(object):
    def __init__(self,options=None):
        try:
            pygame.init()
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        except:
            print('unable to connect to Xbox Controller')
            
            
    def read(self):
        pygame.event.pump()
        L_x_axis = self.joystick.get_axis(0)
        L_y_axis = self.joystick.get_axis(1)
        a_btn = self.joystick.get_button(1)
        b_btn = self.joystick.get_button(2)
        # top buttons
        rb = self.joystick.get_button(5)
        return [L_x_axis, L_y_axis, a_btn, b_btn, rb]
    def manual_override(self):
        pygame.event.pump()
        return self.joystick.get_button(4) == 1
        

class Process(object):
    
    def gamepadImageMatcher(path):
        INRO =\
        """
        SAW -- matches gamepad csv data rows to images based on timestamps
        Returns two matching arrays
        """
	
    	  # Open CSV for reading
    	  csv_path = os.path.join(path, "data.csv")
    	  print ("about to open: {}".format(csv_path))
    	  csv_io = open(csv_path, 'r')
    	  print ("csv successfully opened")
    	
    	  # Convert to a true array
    	  csv = []
    	  for line in csv_io:
    		# Split the string into array and trim off any whitespace/newlines in elements
    		csv.append([item.strip() for item in line.split(',')])
    
    	  if not csv:
    		print ("CSV HAS NO DATA");
    		return None, None
    	
    	# Get list of images in directory and sort it
    	all_files = os.listdir(path)
    	print ("all_files: {}".format(all_files))
    	#images = [image for image in all_files if any(image.endswith('.png'))]
    	images = []
    	for filename in all_files:
    		if filename.endswith('.png'):
    			images.append(filename)
    	images = sorted(images)
    	print ("sorted images list: {}".format(images))
    
    	if not images:
    		print ("FOUND NO IMAGES");
    		return None, None
    
    	# We're going to build up 2 arrays of matching size:
    	keep_csv = []
    	keep_images = []
    	
    	# Prime the pump (queue)...
    	prev_line = csv.pop(0)
    	prev_csvtime = int(prev_line[0])
    	print ("line 0: {}".format(prev_line))
    	
    #            prev_image = images[0]
    #            prev_imgtime = 0
    	
    	# Find next matching image
    	while images:
    		imgfile = images[0]
    		print ("imgfile: {}".format(imgfile))
    		
    		# Get image time:
    		#     Cut off the "gamename-" from the front and the ".png" from the end
    		hyphen = imgfile.rfind('-') # Get last index of '-'
    		if hyphen < 0:
    			print ("UNEXPECTED FILENAME, ABORTING: {}".format(imgfile))
    			break
    		imgtime = int(imgfile[hyphen+1:-4]) # cut it out!
    		print ("imgtime: {}".format(imgtime))
    		
    		lastKeptWasImage = False # Did we last keep an image, or a line?
    	
    		if imgtime > prev_csvtime:
    			print ("keeping image: {}".format(imgtime))
    			keep_images.append(imgfile)
    			del images[0]
    			lastKeptWasImage = True
    			
    			# We just kept an image, so we need to keep a
    			# corresponding input row too
    			while csv:
    				line = csv.pop(0)
    				print ("line: {}".format(line))
    				
    				# Get CSV line timestamp:
    				csvtime = int(line[0])
    				print ("csvtime: {}".format(str(csvtime)))
    				
    				if csvtime >= imgtime:
    					# We overshot the input queue... ready to
    					# keep the previous data line
    					print ("keeping line: {}".format(prev_csvtime))
    					keep_csv.append(prev_line)
    					lastKeptWasImage = False
    					
    				prev_line = line
    				prev_csvtime = csvtime
    				
    				if csvtime >= imgtime:
    					break;
    					
    			if not csv:
    				print ("OUT OF CSV DATA")
    				if lastKeptWasImage:
    					print ("keeping line: {}".format(prev_csvtime))
    					keep_csv.append(prev_line)
    				break
    				
    		else:
    			print ("dropping image: {}".format(imgtime))
    			del images[0]
    		
    	print ("len(keep_data): {}".format(len(keep_csv)))
    	print ("len(keep_images): {}".format(len(keep_images)))
    #	self.print_console("MATCHED RESULTS COUNT: {} <--> {}".format(len(keep_csv),len(keep_images)))
    
    	return keep_csv, keep_images
        
class Trainer(AGBlank):
    """AG_Recorder Widget of MuPen64 Python Ui"""
    def __init__(self, parent, worker):
        # init
        super().__init__(parent)
        self.setWorker(worker)
        try:
            self.pad = xpad()
        except:
            print("Going without it")
        # set up the blanks
        self.setWindowTitle('AG Trainer')
        self.selectorLabel.setText('Existing Save Folders:')
        self.inputLabel.setText('Save to:')
        self.actionButton.setText('Record')
        self.actionButton.setEnabled(False)
        self.checkButton.setEnabled(False)
        self.input.setEnabled(False)
        self.selector.setEnabled(False)
        # timer state
        self.runningTimer = False
        # booleans are good
        self.recording = False # are we recording?
        self.recordStartedAt = None # when did the recording start?
        self.game_on = False   # is there a game runnning?
        # preset some globals
        self.selectedSaveName = None
        self.path = "./"
        
        # setWorker() above already sets self.work_dir
        #self.work_dir = "/tmp"
        
        self.check_game_name = ""
        # startup
        self.print_console("AlphaGriffin.com")
        self.print_console(INTRO)
        
        # Defer startup timers, etc. until after we actually need something to
        # happen, i.e. when the dialog is actually shown.
        #self.startup()
        
        

    """ EASY GOOD WORKING FUNC's """
    def print_console(self, msg): 
        """Takes a String and prints to console"""
        self.console.moveCursor(QTextCursor.End)
        self.console.insertPlainText("{}\n".format(msg))
        #print(msg)
        
    def set_save_dir(self):
        """Sets the Input Field text"""
        #print ("in set_save_dir()")
        name = self.getGame()
        name_path = os.path.join(self.work_dir, name)
        if not os.path.isdir(name_path):
            print ("path does not exist, creating it now: {}".format(name_path))
            os.makedirs(name_path)
        self.print_console("Good Choice with {}, Good luck!".format(name))
        
        self.build_selector(name_path)
        
        l = len(os.listdir(name_path))
        path = "newGame_{}".format(l)
        self.input.setText(os.path.join(name_path,path))
        self.actionButton.setEnabled(True)
        
    def build_selector(self, folder):
        """This populates the save folder list"""
        self.selector.clear()
        for i in sorted(os.listdir(folder)):
            x = "{}".format(i)
            self.selector.addItem(x)
        self.selector.addItem("Record a New Game")
        
    def save_data(self,test=False):
        """Create and populate a data.csv which is the paddle controls and index and timestamp"""
        # screen shots go to a preset place
        #self.worker.save_screenshot() # works good getting every 10th is frame...
        paddle_read = self.pad.read()
        stamp = int(time.time() * 1000)
        y = ("{}:\t{}".format(stamp,paddle_read))
        if test is False:
            # make / open outfile
            outfileName = os.path.join(self.save_name, 'data.csv')
            print("".format(outfileName))
            outfile = open(outfileName, 'a')
            # write line
            outfile.write('{},{}\n'.format(stamp, ','.join(map(str, paddle_read))))
            outfile.close()
        self.print_console(y)
        
    def setWorker(self, worker):
        """Get Worker(ref) from main code and check the local Userdata folder"""
        self.worker = worker
        self.work_dir = self.worker.core.config.get_path("UserData")
        
    def getGame(self):
        """Check if game has been selected and set a dir if it has"""
        x = self.check_game_name = self.worker.core.rom_header.Name.decode().replace(" ", "_").lower()
        if x is not "":
            return x
        return "no_game"
    
    # DEPRICATED!
    def selector_change(self):
        """this reads the selector selection and acts on it."""
        #self.set_save_dir()
        #self.check_tail(self.selectedSaveName)
        pass
     
    # DEPRICATED!
    def check_tail(self, path):
        """Read and print from the CSV file if it exists"""
        x = '{}/{}/data.csv'.format(self.work_dir,path)
        if check(x):
            df = pd.read_csv(x)
            top = df.head(5)
            bottom = df.tail(10)
            concatenated = pd.concat([top,bottom])
            self.print_console("This looks like an Unprocessed Folder\n{}\nRecord in another Dir".format(concatenated))
        else:
            self.print_console("file!=\t{}\nNo Previous Save in this Directory\n\tGame ON!".format(x))
                 
    def startupTimer(self):
        """Start a timer if none is running and keep checking back"""
        # start game checker
        if self.runningTimer == False:
            #self.print_console("Startup Timer is starting at 200 millis..")
            self.runningTimer = QTimer(self)
            self.runningTimer.timeout.connect(self.check_game) # takes the pick and saves data
            self.runningTimer.start(200)    # in millis
                 
    def shutdownTimer(self):
        """Shuts down the timer when we don't need it (dialog hidden, etc.)"""
        if not self.runningTimer == False:
            self.runningTimer.stop()
            self.runningTimer = False
            
            
    def check_game(self):
        """Check mupen worker and see if hes working, called by runningTimer"""
        #x = self.worker.core_state_query(1)
        wasloaded = self.game_on
        self.worker.core_state_query(1)
        loaded = self.worker.state in [2, 3]
        self.game_on = loaded
            
        #self.selector.setEnabled(loaded)
        #self.input.setEnabled(loaded)
        
        if not loaded:
            if wasloaded:
                self.actionButton.setEnabled(False)
            if self.recording:
                self.stop()
        
        if not wasloaded:
            if loaded:
                self.set_save_dir()
        
        # Leave the timer running... it will keep watching the emulator status for us
                
        #if loaded:
        #    self.startupTimer.stop()
        #    self.startupTimer = False
        #    self.set_save_dir()
    
    """
    Test functions 
    """         
    """
    def show(self):
        self.refresh()
        super().show()
    def populate_selector(self):
        self.selector.clear()
        self.work_dir = self.worker.core.config.get_path("UserData")
        print ("work_dir: {}".format(self.work_dir))
        self.check_game_name = self.worker.core.rom_header.Name.decode().replace(" ", "_").lower()
        print ("check_game_name: {}".format(self.check_game_name))
        path = self.work_dir + "/" + self.check_game_name
        print ("path: {}".format(path))
    def update_(self):
        ###This is the timer driven function for saving data to the csv file and capturing images
        x = self.pad.read()
        stamp = int(time.time() * 1000)
        y = ("{}:\t{}".format(stamp,x))
        self.print_console(y)
        
    def check_worker(self): 
        self.work_dir = self.worker.core.config.get_path("UserData")
        self.check_game_name = self.worker.core.rom_header.Name.decode().replace(" ", "_").lower()
        d = os.listdir(self.work_dir)
        self.populate_selector(d)
    def refresh(self, skipItem=None):
        print ("refreshing state")
        loaded = False
        self.worker.core_state_query(1)
        loaded = self.worker.state in [2, 3]
        print ("game loaded: {}".format(loaded))
        sitems = self.selector.selectedItems()
        print ("sitems: {}".format(sitems))
        selected = loaded and sitems is not None and len(sitems) > 0
        print ("selected: {}".format(selected))
        
        self.input.setEnabled(selected)
        self.actionButton.setEnabled(selected)
        if skipItem is not self.selector: self.selector.setEnabled(loaded) 
        
        if loaded and skipItem is not self.selector:
            print ("populating...")
            self.populate_selector()
        
    
    def Check_game_stats(self):
        self.worker.core_state_query(M64CORE_EMU_STATE)
        if self.worker.state in [M64EMU_RUNNING, M64EMU_PAUSED]:
            self.check_worker()
        if self.check_game_name is not "":
            self.work_dir = os.path.join(self.work_dir,self.check_game_name)
        self.print_console(self.work_dir)
    """ 
        
    
        
    def record(self):
        """this starts the recording timer and actionable function"""
        self.actionButton.setText('Stop')
        self.save_name = self.input.text()
        
        if not os.path.isdir(self.save_name):
            os.makedirs(self.save_name)
        
        self.poll_time = QTimer(self)
        self.poll_time.timeout.connect(self.save_data) # takes the pick and saves data
        self.poll_time.start(50)    # in millis
        self.worker.toggle_autoshots()
        self.recording = True
        self.recordStartedAt = time.time()*1000.0
        
    def stop(self):
        #autoshots
        """This ends the recording session and buttons up the screenshot dir"""
        self.poll_time.stop()
        self.worker.toggle_autoshots()
        self.actionButton.setText('Record')
        
        elapsed = time.time()*1000.0 - self.recordStartedAt
        self.print_console("Recording took {} seconds".format(elapsed/1000.0))
        self.recordStartedAt = None
        
        self.set_save_dir()
        self.recording = False
        self.get_images()
        
        
        
    def get_images(self):
        """This moves all the screenshots to the current save_dir"""
        print ("in get_images()")
        shot_dir = os.path.join(self.work_dir,"screenshot/")
        print ("about to list dir: {}".format(shot_dir))
        x = os.listdir(shot_dir)
        print ("got stuff: {}".format(x))
        if len(x) > 0:
            y = []
            for i in x:
                y.append(i)
                #print(shot_dir+i)
                
                mv_from = shot_dir+i
                mv_to = self.save_name
                print ("moving: {} -> {}".format(mv_from, mv_to))
                shutil.move(mv_from, mv_to)
            self.print_console("Got {} images, moved to {}".format(len(y),self.save_name))
            
            #
            # SAW - this is where gamepadImageMatcher stuff happened
            # (now in tf_utils/trainutils.py)
            #
            
        else:
            self.checkButton.setEnabled(True)
            self.print_console("No ScreenShots Saved")
        
    
            
            
    def show(self):
        self.startupTimer()
        super().show()
        
    def hide(self):
        self.shutdownTimer()
        self.stop()
        super().hide()

    ###
    ###  These Slots are set in the UI designer and need to be reset here
    ###
    @pyqtSlot()
    def on_actionButton_clicked(self):
        """Start - Stop record button"""
        if not self.recording: self.record()
        else: self.stop()
        
    @pyqtSlot()
    def on_checkButton_clicked(self):
        """Test Button for pressing broken parts"""
        self.get_images()
    
    # This does not happen in the RECODING CONSOLE anymore        
    @pyqtSlot()
    def on_selector_itemSelectionChanged(self):
        self.selected = self.selector.selectedItems()
        self.selector_change()
        
    @pyqtSlot()
    def closeEvent(self,event=False):
        self.stop()
        super().closeEvent()
