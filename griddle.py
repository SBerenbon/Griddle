#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PIL import Image, ImageDraw, ImageColor, ImageFont
from pyora import Project, TYPE_LAYER
import zipfile
import shutil

global fontFile
fontFile="DroidSansMono.ttf"

def drawGrid(image, color, squareSize=94):
	draw=ImageDraw.Draw(image)
	i=1
	while (squareSize*i)<=image.size[1]:
		draw.line((0, squareSize*i, image.size[0], squareSize*i), fill=color)
		i+=1
		
	j=1
	while (squareSize*j)<=image.size[0]:
		draw.line((squareSize*j, 0, squareSize*j, image.size[1]), fill=color)
		j+=1
	return image

def drawCoords(image, squareSize=94, color="black"):
	draw=ImageDraw.Draw(image)
	midwayPoint=int(squareSize/2)
	y=0
	x=0
	while (midwayPoint+y*squareSize)<=image.size[1]:
		x=0
		while (midwayPoint+x*squareSize)<=image.size[0]:
			#make the text bigger, related to the squareSize
			scaleFont = ImageFont.truetype(fontFile, size=int(squareSize*.25))
			a=draw.text((x*squareSize, (midwayPoint+y*squareSize)), "x"+str(x+1)+"y"+str(y+1), fill=color, font=scaleFont)
			x+=1
		y+=1
	return image

def makeBlankFromImage(sourceImage):
	baseCanvas=Image.new("RGBA", sourceImage.size, "white")
	canvasData = baseCanvas.getdata()
	canvas=[]
	for pixel in canvasData:
		if pixel[0] == 255 and pixel[1] == 255 and pixel[2] == 255:
			# replacing it with a transparent value
			canvas.append((255, 255, 255, 0))
		else:
			canvas.append(pixel)
	baseCanvas.putdata(canvas)
	return baseCanvas

def cutByGrid(image, folder, squareSize=94):
	#imageCut = image.crop((left, top, right, bottom)) 
	fromX=0
	fromY=0
	currentX=0
	currentY=0
	toX=0
	toY=fromY+squareSize
	grzFileName=folder
	if grzFileName[-1]==os.path.sep:
		grzFileName=grzFileName[:-1]
	grzFolderName=grzFileName.split(os.path.sep)[-1]
	grzFile=zipfile.ZipFile(grzFileName+".grz", "w", zipfile.ZIP_DEFLATED)
	#there will have to be some resetting!
	#it will terminate once it has cut the lower right hand corner square, toX and toY are equal to image.size[0] and image.size[1]
	#while not (toX==image.size[0] and toY==image.size[1]):
	while True:
		toX=fromX+squareSize
		#I increment currentX every run
		if toX>image.size[0]:
			toX=image.size[0]
		if toY>image.size[1]:
			toY=image.size[1]
		#print((fromX, fromY, toX, toY))
		#left, top, left+width, top+height
		imageCut = image.crop((fromX, fromY, toX, toY))
		#pad these - and if I already have a padding function, put it in benri!
		squareFileName=os.path.join(folder, "x"+str(currentX+1)+"_y"+str(currentY+1)+".png")
		imageCut.save(squareFileName, "PNG")
		grzPath=os.path.join(grzFolderName, squareFileName.split(os.path.sep)[-1])
		grzFile.write(squareFileName, grzPath)
		if toX>=image.size[0]:
			if toY>=image.size[1]:
				break
			else:
				currentX=0
				currentY+=1
				fromY=toY
				toY=fromY+squareSize
				fromX=0
			#reset currentX to 0, then it's time to increment Y and start again
		else:
			currentX+=1
			fromX=toX
	#the folder is zipped and full, bam, Griddle archive
	shutil.rmtree(folder)

import os.path, argparse

def main(pics, squareSize, squareColor, canvasColor, canvasSquareColor, resizePercentage, outputFiles=False):
	resizePercentageOriginal=resizePercentage
	resizePercentage*=.01
	for pic in pics:
		extension=os.path.splitext(pic)[1].lower()
		if extension.lower() in [".png", ".jpeg", ".jpg", ".gif", ".webp", ".bmp", ".ppm"]:
			pic=os.path.abspath(pic)
			sourceFolder=os.path.dirname(pic)
			sourceImageName=os.path.basename(pic)
			sourceImage=Image.open(pic)
			#Thanks to https://stackoverflow.com/questions/68365846/pillow-np-how-to-convert-transparent-mapped-indexed-png-to-rgba-when-transpar
			if sourceImage.mode=="P":
				is_transparent = sourceImage.info.get("transparency", False)
				if is_transparent is False:
					# if not transparent, convert indexed image to RGB
					sourceImage = sourceImage.convert("RGB")
				else:
					# convert indexed image to RGBA
					sourceImage = sourceImage.convert("RGBA")
			elif sourceImage.mode=="PA":
				sourceImage=sourceImage.convert("RGBA")
			if resizePercentage!=1:
				sourceImage=sourceImage.resize((int(sourceImage.size[0]*resizePercentage), int(sourceImage.size[1]*resizePercentage)))
				sourceImageName=str(int(resizePercentageOriginal))+"scale"+"_"+sourceImageName
			
			canvasBackgroundLayer=Image.new("RGBA", sourceImage.size, canvasColor)
			destOra = Project.new(sourceImage.size[0], sourceImage.size[1])
			destOra.add_group('/Painting', composite_op='svg:src-over')
			destOra.add_layer(canvasBackgroundLayer, 'Painting/BackgroundCanvas')
			destOra.add_layer(makeBlankFromImage(sourceImage), 'Painting/BackgroundColor')
			destOra.add_layer(makeBlankFromImage(sourceImage), 'Painting/Canvas')
			destOra.add_layer(makeBlankFromImage(sourceImage), 'Painting/Ink')
			destOra.add_layer(makeBlankFromImage(sourceImage), 'Painting/Color')
			
			gridCanvas=makeBlankFromImage(sourceImage)
			destImageGrid=drawGrid(gridCanvas, canvasSquareColor, squareSize)
			#can we put a blank layer on top of this, and write it to ORA?
			#guess not, ah well
			#well, with pyora
			if outputFiles:
				destImageGrid.save(os.path.join(sourceFolder, "dest_grid_"+sourceImageName), "PNG")
			destOra.add_layer(destImageGrid, 'Painting/Grid')
			ora = [destImageGrid]

			coordsCanvas=makeBlankFromImage(sourceImage)
			destImage=drawCoords(coordsCanvas, squareSize, canvasSquareColor)
			if outputFiles:
				destImage.save(os.path.join(sourceFolder, "dest_coords_"+sourceImageName), "PNG")
			destOra.add_layer(destImage, 'Painting/Coords')

			newFolder=os.path.join(sourceFolder, os.path.splitext(sourceImageName)[0])
			if not os.path.exists(newFolder):					
				os.mkdir(newFolder)
			cutByGrid(sourceImage, newFolder, squareSize)
				#make this transparent, so I can use both the coords grid and the other grid!
				#make the other one transparent too
				#make the file, then write it
			#print(destOra.dimensions)
			destOra.save(os.path.join(sourceFolder, "dest_"+os.path.splitext(sourceImageName)[0]+".ora"))
			#if outputFiles:
			gridImage=drawGrid(sourceImage, squareColor, squareSize)
			gridImage.save(os.path.join(sourceFolder, "source_"+sourceImageName), "PNG")
			#the ora file I want has a single group, with a painting layer, a coords layer, and a simple grid layer

parser = argparse.ArgumentParser(description="Put grids on images and canvases to make drawing them easier")
parser.add_argument("-s", "--squareSize", type=int, help="Set the size of the boxes, and the colors of the boxes on the source image, at least 1", default=94)
parser.add_argument("-c", "--squareColor", help="English or hex", default="blue")
parser.add_argument("-a", "--canvasColor", help="English or hex", default="white")
parser.add_argument("-q", "--canvasSquareColor", help="English or hex", default="black")

parser.add_argument("-z", "--resize", type=float, help="Percentage to resize to")
#parser.add_argument("-H", "--chop", help="Cut the source into multiple smaller images, best with big pictures", action='store_true')
parser.add_argument("-O", "--output", help="Output the grid and coordinates to their own files", action='store_true')
parser.add_argument("-d", "--dark", help="Make a black canvas with white decs", action='store_true')
parser.add_argument("pics", nargs="+", help="Images to work on")

#I could make an argument to specify square size, and ones to specify colors
if __name__ == "__main__":
	if len(sys.argv[1:]):
		squareSize=94
		squareColor="blue"
		canvasColor="white"
		canvasSquareColor="black"
		resizePercentage=100
		outputFiles=False
		darkMode=False
		args = parser.parse_args()
		if args.squareSize:
			squareSize=args.squareSize
		if args.resize:
			resizePercentage=args.resize
		if args.squareColor:
			args.squareColor=args.squareColor.lower()
			if args.squareColor in ImageColor.colormap:
				squareColor=args.squareColor
			elif args.squareColor in ImageColor.colormap.values():
				squareColor=args.squareColor
			elif "#"+args.squareColor in ImageColor.colormap.values():
				squareColor="#"+args.squareColor
			else:
				print("Invalid square color, defaulting to blue...")
		if args.canvasColor:
			args.canvasColor=args.canvasColor.lower()
			if args.canvasColor in ImageColor.colormap:
				canvasColor=args.canvasColor
			elif args.squareColor in ImageColor.colormap.values():
				canvasColor=args.canvasColor
			elif "#"+args.squareColor in ImageColor.colormap.values():
				canvasColor="#"+args.canvasColor
			else:
				print("Invalid canvas color, defaulting to white...")
		if args.canvasSquareColor:
			args.canvasSquareColor=args.canvasSquareColor.lower()
			if args.canvasSquareColor in ImageColor.colormap:
				canvasSquareColor=args.canvasSquareColor
			elif args.canvasSquareColor in ImageColor.colormap.values():
				canvasSquareColor=args.canvasSquareColor
			elif "#"+args.canvasSquareColor in ImageColor.colormap.values():
				canvasSquareColor="#"+args.canvasSquareColor
			else:
				print("Invalid canvas square color, defaulting to black...")
		if len(args.pics):
			pics=args.pics
			if args.output:
				outputFiles=True
			if args.dark:
				squareColor="white"
				canvasColor="black"
				canvasSquareColor="white"
			main(pics, squareSize, squareColor, canvasColor, canvasSquareColor, resizePercentage, outputFiles)
	else:
		sys.exit()
