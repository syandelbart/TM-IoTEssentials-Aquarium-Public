# Aquarium
## Introduction
This project was made for the course "IoT Essentials" at Thomas More. The purpose was to show your knowledge regarding GPIO and a basic understanding of Python. I worked with different components (stepper motor, ultrasonic sensor, lcd, buttons). Some other functions were implemented such as phone control, live stream and uploading component data to Ubeac.

## The code
The code isn't perfectly optimized. The idea was to keep it readable but functional as well. The [complete code](https://github.com/syandelbart/TM-IoTEssentials-Aquarium-Public/blob/39d13a232f90d73d33709c2a4207e6071885a97d/final.py) can be found on GitHub.
```js
ps_checkbuttons = Process(target = getButtonPresses)
ps_checkbuttons.start()

#Set the timeout for the motor moving (=automatic feeding)
motor_timeout = 60 * 60 * 12
motor_now = ""

while True:
    getCurrentTime()
    getUltrasonicReadings()
    getLampState(False,True)
    if not motor_now or time.time() - motor_now > motor_timeout:
        motorMove(motor_steps_total * 1/4,True)
        motor_now = time.time()
        motor_next_feed = time.localtime(motor_now + motor_timeout)
        drawRow(1,nextfeed + str(motor_next_feed.tm_hour) + ":" + str(motor_next_feed.tm_min))
```
The most important part is the main code. This code will first create a new process for `ps_checkbuttons`, otherwise button input would have a serious delay as it would have to wait for each other function to execute. Below that a `motor_timeout` will be defined which will define the amount of time in between rotations (for feeding the fish). Lastly the program will loop over functions to update the current time, update the distance measured and the lamp state and print all these updated values to the LCD.

## Evaluation criteria

| Functionality  | Points |
| ------------- | ------------- |
| Stepper motor drops food | 2.5
| Ultrasonic measurement of depth | 2.5
| Pump and light turn on/off  | 2.5
| Buttons  | 2.5
| LCD  | 2
| Ubeac upload  | 2
| Live stream  | 2
| Phone control  | 2
| Nice physical setup  | 2
| **Total** | **20**
