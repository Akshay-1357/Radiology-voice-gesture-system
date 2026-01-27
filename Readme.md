# Multimodal Voice & Gesture Controlled Radiology System

INTRODUCTION

Imaging devices involve radiation, and this is made use of by radiology techs. The authors of this project built a voice-command and hand-gesture controlled system for remote control of radiology systems by the technicians from outside high radiation zones. Voice and hand gestures are recognized for voice/gesture recognition by python, commands are executed in ESP32 controller, thereby enhancing safety and efficiency of operations.

STRATEGIC INTENT:

a.Reduce radiation exposure to technicians.

b.Enable remote, hands-free machine control.

c.Improve safety and workflow efficiency.

LOGIC FLOW:

Voice commands and hand-wave gestures are captured using a microphone and camera. These inputs are processed using Python for voice and gesture recognition. The processed commands are then sent to an Arduino UNO via serial communication, which executes the required control actions.

ACTION ITEMS:

1.HARDWARE:

        a.1 × Arduino UNO
        b.USB Cable (USB-A to Micro-USB / Type-C) – 1
        c.Computer/Laptop with microphone and camera 

2.SOFTWARE:

        a.Python 3.x
        b.Arduino IDE
        c.Python Libraries we used: SpeechRecognition, OpenCV, MediaPipe and NumPy

EXECUTION:

        a.Capture voice commands using a microphone.
        b.Detect hand gestures using a camera.
        c.Process commands in Python.
        d.Send control commands to Arduino UNO via serial communication.
        e.Execute control actions through Arduino UNO. 

INTERFACE:

        a.Radiology and medical imaging rooms
        b.Hands-free equipment control
        c.Hazardous environment operation

CONCLUSION

This project provides a simple and effective solution for safely operating radiology machines using voice and hand gestures, reducing radiation exposure and improving technician safety.