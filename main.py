from TempPressureSensor import tempPressure
from time import sleep
import picamera
import threading

#thread the camera so in the event of IO errors it can be automatically restarted
class threadedCamera(threading.Thread):
  def __init__(self):
    self.endThread = False
    
    #super constructor
    super(threading.Thread, self).__init__()
    
  def run(self):
    #create a new camera object and use a with stmnt to ensure the IO closes cleanly
    with picamera.PiCamera() as camera:
      #use the maximum avaiable image resolution
      camera.resolution = (2592, 1944)
      
      camera.start_preview()
      sleep(2)
      
      #generator object for filenames e.g. "image-12:01"
      for fp in camera.capture_continuous("image-{timestamp:%H:%M}.jpg"):
        print "Image Captured"
        for i in range(0, 120):
          sleep(1)
          if self.endThread == True: return
        
   def join(self):
     #end the mainloop and wait for it to exit cleanly
     print "Terminating %s Thread" % (self.__class__.__name__)
     self.endThread = True
     sleep(2)
     super(threading.Thread, self).join()
     
#thread the temp sensor so in the event of IO errors it can be automatically restarted
class tempPressureThread(threading.Thread):
  def __init__(self):
    self.tempPressure = tempPressure()
    self.tempPressure.createFile()
    self.end = False
    threading.Thread.__init__(self)
    
  def run(self):
    while not self.end:
      self.tempPressure.getResults()
      self.tempPressure.writeData()
      print "Temperature:", self.tempPressure.temp, "Pressure:", self.tempPressure.pressure
      sleep(120)
      
  def join(self):
    self.end = True
    threading.Thread.join(self)
     
myCamera = threadedCamera()
myCamera.start()

myTempPressure = tempPressureThread()
myTempPressure.start()

while True:
  try:
    #make sure that the camera thread is still running and has not crashed
    if myCamera.isAlive() == False:
      myCamera.join()
      myCamera = threadedCamera()
      myCamera.start()
      
    #make sure that the temp pressure thread is still running and has not crashed
    if myTempPressure.isAlive() == False:
      myTempPressure.join()
      myTempPressure = tempPressureThread()
      myTempPressure.start()
      
  except KeyboardInterrupt as e:
    #end the program
    print "Exiting..."
    myCamera.join()
    break
    
