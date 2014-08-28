import os
import sys
from xlwt import *
import xlwt
from base import from_this_dir

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
#to write a simple file you just need the xlwt package.


wb = Workbook() # create empty workbook object
newsheet = wb.add_sheet('colorful_words') #adding and renaming a column

red = xlwt.easyxf('font: bold 1, color red') 
blue = xlwt.easyxf('font: bold 1, color blue') 
green = xlwt.easyxf('font: bold 1, color green') 
brown = xlwt.easyxf('font: bold 1, color brown') 

newsheet.write(0,0,'Hello', red) #write in the first cel A1
newsheet.write(0,1,'World!', blue) #write in B1
newsheet.write(1,0,'I am', green) #write in A2
newsheet.write(1,1,'learning', brown) #write in B2

wb.save(from_this_dir('03_formating.xls'))