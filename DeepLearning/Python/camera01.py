#!/usr/bin/python3
#
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

import RPi.GPIO as GPIO
import jetson.inference
import jetson.utils

import time

import argparse
import sys

# parse the command line
parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", 
                                 formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.detectNet.Usage() +
                                 jetson.utils.videoSource.Usage() + jetson.utils.videoOutput.Usage() + jetson.utils.logUsage())

parser.add_argument("input_URI", type=str, default="", nargs='?', help="URI of the input stream")
parser.add_argument("output_URI", type=str, default="", nargs='?', help="URI of the output stream")
parser.add_argument("--network", type=str, default="ssd-mobilenet-v2", help="pre-trained model to load (see below for options)")
parser.add_argument("--overlay", type=str, default="box,labels,conf", help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are:  'box', 'labels', 'conf', 'none'")
parser.add_argument("--threshold", type=float, default=0.5, help="minimum detection threshold to use") 

is_headless = ["--headless"] if sys.argv[0].find('console.py') != -1 else [""]

try:
	opt = parser.parse_known_args()[0]
except:
	print("")
	parser.print_help()
	sys.exit(0)

# load the object detection network
net = jetson.inference.detectNet(opt.network, sys.argv, opt.threshold)

# create video sources & outputs
input = jetson.utils.videoSource(opt.input_URI, argv=sys.argv)
output = jetson.utils.videoOutput(opt.output_URI, argv=sys.argv+is_headless)

#setup GPIO pins

GPIO.setmode(GPIO.BCM) #RaspPi pin numbering

GPIO.setup(18, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(23, GPIO.OUT, initial=GPIO.LOW)

GPIO.setup(17, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(22, GPIO.OUT, initial=GPIO.LOW)

def forward():
	GPIO.output(18, GPIO.LOW)		
	GPIO.output(23, GPIO.HIGH)
	GPIO.output(17, GPIO.LOW)
	GPIO.output(22, GPIO.HIGH)

def backward():
	GPIO.output(18, GPIO.HIGH)		
	GPIO.output(23, GPIO.LOW)
	GPIO.output(17, GPIO.HIGH)
	GPIO.output(22, GPIO.LOW)

def stop():
	GPIO.output(18, GPIO.LOW)		
	GPIO.output(23, GPIO.LOW)
	GPIO.output(17, GPIO.LOW)
	GPIO.output(22, GPIO.LOW)

def right():
	GPIO.output(18, GPIO.HIGH)		
	GPIO.output(23, GPIO.LOW)
	GPIO.output(17, GPIO.LOW)
	GPIO.output(22, GPIO.HIGH)

def left():
	GPIO.output(18, GPIO.LOW)		
	GPIO.output(23, GPIO.HIGH)
	GPIO.output(17, GPIO.HIGH)
	GPIO.output(22, GPIO.LOW)

# declare variables as global and that

global index
global width
global location
global flag
index = 0
width = 0
location = 0
flag = 0

# process frames until the user exits
while True:	

	# capture the next image
	img = input.Capture()

	# detect objects in the image (with overlay)
	detections = net.Detect(img, overlay=opt.overlay)

	# print the detections
	#print("detected {:d} objects in image".format(len(detections)))
	

	for detection in detections:
		index = detections[0].ClassID
		width = (detections[0].Width)
		location = (detections[0].Center[0])

	# print index of item, width and horizonal location

	print("detection:")
	print(index)
	print(width)
	print(location)
	print(flag)

	# hunt for the detected objects in order

	# look for item number 1

	if (index != 1 and flag == 0):
		left()
	elif(index == 1 and location > 600 and location < 700 and flag == 0):
		flag = 1
	elif (flag == 1 and width < 600):
		forward()
	elif (flag == 1 and width > 600):
		stop()
		flag = 2

	# look for item number 2

	elif (index != 2 and flag == 2):
		left()
	elif(index == 2 and location > 600 and location < 700 and flag == 2):
		flag = 3
	elif (flag == 3 and width < 600):
		forward()
	elif (flag == 3 and width > 600):
		stop()
		flag = 4

	# look for item number 3

	elif (index != 3 and flag == 4):
		left()
	elif(index == 3 and location > 600 and location < 700 and flag == 4):
		flag = 5
	elif (flag == 5 and width < 600):
		forward()
	elif (flag == 5 and width > 600):
		stop()
		flag = 0




	# render the image
	output.Render(img)

	# update the title bar
	output.SetStatus("{:s} | Network {:.0f} FPS".format(opt.network, net.GetNetworkFPS()))

	# print out performance info
	#net.PrintProfilerTimes()

	# exit on input/output EOS
	if not input.IsStreaming() or not output.IsStreaming():
		break


