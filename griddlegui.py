#!/usr/bin/env python
# -*- coding: utf-8 -*-

from traceback import print_exc

import wx
import os, os.path
import sys
import glob

import griddle
from PIL import ImageColor
wildcard = "Images|*.png;*.PNG;*.jpg;*.JPG;*.jpeg;*.JPEG;*.gif;*.GIF;*.ppm;*.PPM;*.webp;*.WEBP;*.bmp;*.BMP"

from benrifunctions import *

currentdirectory=os.getcwd()#sys.path[0]

#when you load the file, print a preview name

#I need a dropdown with the pictures
#maybe an input box for whatever color in hex
#a number input box for the square size

class TheWindow(wx.Panel):
	def __init__(self, parent, id):
	#create the panel
		wx.Panel.__init__(self, parent, id)
		self.bigsizer=wx.BoxSizer(wx.VERTICAL)
		self.squaresizer=wx.BoxSizer(wx.HORIZONTAL)
		
		self.SquareSizeLabel=wx.StaticText(self, label="Square Size:")
		#I'm not specifying a max, you know your needs, and the limits of your computer better than me, future me
		self.SquareSize=wx.SpinCtrl(self, -1, "92", min=1)
		self.squaresizer.Add(self.SquareSizeLabel, 1)
		self.squaresizer.Add(self.SquareSize, 1)
		
		self.squarecolorsizer=wx.BoxSizer(wx.HORIZONTAL)
		
		self.ValidColors=list(ImageColor.colormap.keys())

		self.SquareColorLabel=wx.StaticText(self, label="Square Color:")
		self.SquareColorComboBox=wx.ComboBox(self, choices=self.ValidColors, style=wx.CB_DROPDOWN)
		self.SquareColorComboBox.SetSelection(9)#blue
		self.squarecolorsizer.Add(self.SquareColorLabel, 1)
		self.squarecolorsizer.Add(self.SquareColorComboBox, 1)
		

		self.canvassquarecolorsizer=wx.BoxSizer(wx.HORIZONTAL)
		self.CanvasSquareColorLabel=wx.StaticText(self, label="Canvas Square Color:")
		self.CanvasSquareColorComboBox=wx.ComboBox(self, choices=self.ValidColors, style=wx.CB_DROPDOWN)
		self.CanvasSquareColorComboBox.SetSelection(7)#black
		self.canvassquarecolorsizer.Add(self.CanvasSquareColorLabel, 1)
		self.canvassquarecolorsizer.Add(self.CanvasSquareColorComboBox, 1)


		self.canvascolorsizer=wx.BoxSizer(wx.HORIZONTAL)
		
		self.CanvasColorLabel=wx.StaticText(self, label="Canvas Color:")
		self.CanvasColorComboBox=wx.ComboBox(self, choices=self.ValidColors, style=wx.CB_DROPDOWN)
		self.CanvasColorComboBox.SetSelection(144)#white
		self.canvascolorsizer.Add(self.CanvasColorLabel, 1)
		self.canvascolorsizer.Add(self.CanvasColorComboBox, 1)
		
		self.resizersizer=wx.BoxSizer(wx.HORIZONTAL)
		self.ResizePercentageCheck=wx.CheckBox(self, -1, "Resize?")
		self.ResizePercentageCheck.Bind(wx.EVT_CHECKBOX, self.ResizeCheck)
		#grey these out when unchecked?
		self.ResizePercentageLabel=wx.StaticText(self, label="Percentage:")
		#float, though?
		self.ResizePercentage=wx.SpinCtrl(self, -1, "100", min=1)
		self.resizersizer.Add(self.ResizePercentageCheck, 1)
		self.resizersizer.Add(self.ResizePercentageLabel, 1)
		self.resizersizer.Add(self.ResizePercentage, 1)
		self.ResizePercentage.Enabled=False
		
		self.outputsizer=wx.BoxSizer(wx.HORIZONTAL)
		self.OutputCheck=wx.CheckBox(self, -1, "Output Files?")
		self.DarkModeCheck=wx.CheckBox(self, -1, "Dark Mode?")
		self.outputsizer.Add(self.OutputCheck, 1)
		self.outputsizer.Add(self.DarkModeCheck, 1)
		
		self.picturelist = wx.ListBox(self, style=wx.LB_MULTIPLE|wx.LB_NEEDED_SB)
		#self.picturelist.SetBackgroundColour(wx.Colour(255, 255, 128))
		self.button1 = wx.Button(self, label="&Select Pictures")
		self.button1.Bind(wx.EVT_BUTTON, self.BringUpPictures)

		self.button2 = wx.Button(self, label="&Grid Selected")
		self.button2.Bind(wx.EVT_BUTTON, self.GridThePictures)

		self.button3 = wx.Button(self, label="Rem&ove Selected")
		self.button3.Bind(wx.EVT_BUTTON, self.RemoveSelectedPictures)

		self.button4 = wx.Button(self, label="&Clear")
		self.button4.Bind(wx.EVT_BUTTON, self.ClearThePictures)

		self.buttonquit = wx.Button(self, label="&Quit")
		self.buttonquit.Bind(wx.EVT_BUTTON, self.Quitter)

		self.bigsizer.Add(self.squaresizer, 1)
		self.bigsizer.Add(self.squarecolorsizer, 1)
		self.bigsizer.Add(self.canvassquarecolorsizer, 1)
		self.bigsizer.Add(self.canvascolorsizer, 1)
		self.bigsizer.Add(self.resizersizer, 1)
		self.bigsizer.Add(self.outputsizer, 1)
		self.bigsizer.Add(self.picturelist, 6, wx.EXPAND)
		self.bigsizer.Add(self.button1, 1, wx.EXPAND)
		self.bigsizer.Add(self.button2, 1, wx.EXPAND)
		self.bigsizer.Add(self.button3, 1, wx.EXPAND)
		self.bigsizer.Add(self.button4, 1, wx.EXPAND)
		self.bigsizer.Add(self.buttonquit, 1, wx.EXPAND)

		self.SetSizer(self.bigsizer)
		self.SetAutoLayout(True)
		self.Layout()
		try:
			pictures=sys.argv[1:]
			selections = self.picturelist.GetStrings()
			for picture in pictures:
				picture=os.path.abspath(picture)
				
				picturepath,picturefilename=os.path.split(picture)
				extension=os.path.splitext(picturefilename)[1]
				if extension.lower() in [".png", ".jpeg", ".jpg", ".gif", ".webp", ".bmp", ".ppm"]:				
					if picture not in selections:
						self.picturelist.Append(picture)
			if len(self.picturelist.GetStrings())==1:
				self.picturelist.Select(0)
		except:
			pass
			

	def ResizeCheck(self, event):
		if self.ResizePercentageCheck.IsChecked():
			self.ResizePercentage.Enabled=True
		else:
			self.ResizePercentage.Enabled=False

	def BringUpPictures(self, event):
		dlg = wx.FileDialog(None, message="Pick your pictures!", wildcard=wildcard, defaultDir=os.getcwd(), style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR)
		choice=dlg.ShowModal()
		if choice==wx.ID_OK:
			yourpictures=dlg.GetPaths()
			selections = self.picturelist.GetStrings()
			for picture in yourpictures:
				picture=os.path.abspath(picture)
				if picture not in selections:
					self.picturelist.Append(picture)
			if len(self.picturelist.GetStrings())==1:
				self.picturelist.Select(0)

	def ClearThePictures(self, event):
		self.picturelist.Clear()

	def RemoveSelectedPictures(self, event):
		selecti = self.picturelist.GetSelections()
		for i in reversed(list(selecti)):
			self.picturelist.Delete(i)

	def GridThePictures(self, event):
		whatwasstripped=""
		pictures=[]
		selections = self.picturelist.GetSelections()
		for i in selections:
			picture=self.picturelist.GetString(i)
			picturepath,picturefilename=os.path.split(picture)
			extension=os.path.splitext(picturefilename)[1]
			if extension.lower() in [".png", ".jpeg", ".jpg", ".gif", ".webp", ".bmp", ".ppm"]:
				pictures.append(self.picturelist.GetString(i))
		selections=list(reversed(selections))
		sel=0
		resizeTo=100
		if self.ResizePercentage.Enabled:
			resizeTo=int(self.ResizePercentage.GetValue())
		outputOrNot=False
		darkMode=False
		if self.OutputCheck.IsChecked():
			outputOrNot=True
		if self.DarkModeCheck.IsChecked():
			squareColor="white"
			canvasColor="black"
			canvasSquareColor="white"
		else:
			squareColor=self.SquareColorComboBox.GetValue()
			canvasColor=self.CanvasColorComboBox.GetValue()
			canvasSquareColor=self.CanvasSquareColorComboBox.GetValue()
		for picture in reversed(list(pictures)):
			griddle.main([picture], int(self.SquareSize.GetValue()), squareColor, canvasColor, canvasSquareColor, resizeTo, outputOrNot)
			self.picturelist.Delete(selections[sel])
			sel+=1
	def Quitter(self, event):
		dlg=wx.MessageDialog(None, "Are you sure you want to quit?", "Confirm Exit", wx.YES_NO)
		choice=dlg.ShowModal()
		if choice==wx.ID_YES:
			sys.exit()

app = wx.App()
mainframe = wx.Frame(None, -1, "Griddle GUI", size = (600, 540))
# call the derived class
TheWindow(mainframe,-1)
mainframe.Show(1)
app.MainLoop()
