# Unity_UITCar
* Video demo how to use: https://youtu.be/qCGfjkro6qA

_**For Map Test**_
* How to use
  - Open theFxUITCar.x86_64 with ubuntu x64 or x86 with ubuntu x86 (If high performace does not work, please choose the fastest)
    + ./theFxUITCar.x86_64
  - go to folder Unity_UITCar
    + cd Unity_UITCar
  - run the file I made
    + ./bin/autocar
  - Press 0 for changing to manual mode or autopilot mode
  
* For anyone want to make with cmake:
  - in Unity_UITCar folder do:
    + cmake .
    + make
    + ./bin/autocar
 
_**For Round 1**_
* How to use

  _**Python** language_
  - All image processing code should be put in processThread, in run function
  - To change speed and angle, just make speed = (int) and angle = (int)
  - To read current speed feedback from car, just take out rspeed variable
  
  _**C++** language_
  - All image processing code should be put in process function
  - To change speed and angle, just change sATS.angle = (int) and sATS.speed = (int)
  - To read current speed feedback from car, just take out speed variable
  
  _**Json Structure**_
  - {"speed":0,"angle":0,"request":NONE}
  - speed and angle should be int for the best server-side environment processing
  - request:
    + NONE : nothing
    + SPEED : feedback speed
    + ANGLE : feedback angle (this value is not recommended for true processing)

_**For more**_
* Explain
  - In **C++** class JsonParse is for speed and angle build to json then send to server ==> Example from line 87 to line 89
  - In **python** Json is from line 42 to line 44
  - The image file of road line is in TheFxUITCar_Data/Snapshots/ and named: fx_UIT_Car.png
  
** Note
  - To get Ip Address for changing in source code, open unity application and the IP of server is the black text in right side
  - Please change the IPAddress in line 74 of main.cpp to the same with IP of server
  - If **Ubuntu** can not run unity file, chmod +x for that file

** This is still not the final version and still being developed

** If you have any question or need supporting, please contact me.

** Email: fxanhkhoa@gmail.com or 15520364@gm.uit.edu.vn

** Phone: 077 291 297 0
