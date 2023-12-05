#!/usr/bin/env python
# -*- coding: utf-8 -*-
#you'd need the square size to know how big to make the window

import glob, sys
import zipfile
#if there's an argument that's a .grz file, that's actually a Griddle archive zip, open that

import pygame
from pygame.locals import *
import sys
import os
pygame.init()
pygame.display.set_caption("GRZ Viewer")
import argparse
import zipfile
import tempfile

parser = argparse.ArgumentParser(description="Set which square to start on")
parser.add_argument("-x", "--xcoord", type=int, help="X to start at", default=1)
parser.add_argument("-y", "--ycoord", type=int, help="Y to start at", default=1)
parser.add_argument("grz", nargs="?", help="GRZ to open")

squareSize=94
x=1
y=1
args=None
if len(sys.argv[1:]):
	args = parser.parse_args()
	if args.xcoord:
		x=args.xcoord
	if args.ycoord:
		y=args.ycoord
	if args.grz:
		if args.grz.lower().endswith(".grz"):
			theGrz=zipfile.ZipFile(args.grz)
			tempDir = tempfile.gettempdir()
			theGrz.extractall(tempDir)
			squares=theGrz.namelist()
			namesAndSquares = {name.split(os.path.sep)[1]: os.path.join(tempDir, name) for name in theGrz.namelist()}
			theGrz.close()
			
			if len(squares):
				mainloop = True
				screen = pygame.display.set_mode([squareSize,squareSize])
				firstSquare=pygame.image.load(namesAndSquares["x1_y1.png"]).convert()
				firstSquareSize=firstSquare.get_size()[0]
				if squareSize!=firstSquareSize and squareSize not in args:
					squareSize=firstSquareSize
					screen = pygame.display.set_mode([squareSize,squareSize])

				pygame.display.update()
				currentSquareName="x"+str(x)+"_y"+str(y)+".png"
				currentSquare=pygame.image.load(namesAndSquares[currentSquareName]).convert()
				pygame.display.set_caption(currentSquareName)
				while mainloop:
					for event in pygame.event.get():
						if event.type == pygame.QUIT:
							mainloop=False
							sys.exit()

						elif event.type == pygame.KEYDOWN:

							if event.key == pygame.K_ESCAPE:
								mainloop = False
							elif event.key == pygame.K_UP:
								if y>1:
									y-=1
									currentSquareName="x"+str(x)+"_y"+str(y)+".png"
									currentSquare=pygame.image.load(namesAndSquares[currentSquareName]).convert()
									pygame.display.set_caption(currentSquareName)
									print("Changed to square "+currentSquareName)
							elif event.key == pygame.K_DOWN:
								if "x"+str(x)+"_y"+str(y+1)+".png" in namesAndSquares:
									y+=1
									currentSquareName="x"+str(x)+"_y"+str(y)+".png"
									currentSquare=pygame.image.load(namesAndSquares[currentSquareName]).convert()
									pygame.display.set_caption(currentSquareName)
									print("Changed to square "+currentSquareName)
							elif event.key == pygame.K_LEFT:
								if x>1:
									x-=1
									currentSquareName="x"+str(x)+"_y"+str(y)+".png"
									currentSquare=pygame.image.load(namesAndSquares[currentSquareName]).convert()
									pygame.display.set_caption(currentSquareName)
									print("Changed to square "+currentSquareName)
							elif event.key == pygame.K_RIGHT:
								if "x"+str(x+1)+"_y"+str(y)+".png" in namesAndSquares:
									x+=1
									currentSquareName="x"+str(x)+"_y"+str(y)+".png"
									currentSquare=pygame.image.load(namesAndSquares[currentSquareName]).convert()
									pygame.display.set_caption(currentSquareName)
									print("Changed to square "+currentSquareName)
							elif event.key == pygame.K_q:
								mainloop=False
								sys.exit()
					screen.fill([0,0,0])
					screen.blit(currentSquare, (0, 0))
					pygame.display.update()
