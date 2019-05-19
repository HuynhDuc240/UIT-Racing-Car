# Unity_UITCar
* Video demo how to use: https://youtu.be/qCGfjkro6qA
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
  
* Explain
  - Class JsonParse is for speed and angle build to json then send to server ==> Example from line 87 to line 89
  - The image file of road line is in TheFxUITCar_Data/Snapshots/ and named: fx_UIT_Car.png
  
** Note
  - Please run theFxUITCar.x86_64 because that is the server and the IP of server is the black text at right.
  - Please change the IPAddress in line 74 of main.cpp to the same with IP of server.
  - For best result in competition, we will use Fantastic graphic version, so please test with Fantastic version.

** This is still not the final version and still being developed

** If you have any question or need supporting, please contact me.

** Email: fxanhkhoa@gmail.com or 15520364@gm.uit.edu.vn

** Phone: 077 291 297 0
