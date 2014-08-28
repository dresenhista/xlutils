import os
import sys
from xlwt import *

from base import from_this_dir

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
#to write a simple file you just need the xlwt package.


wb = Workbook() # create empty workbook object
newsheet = wb.add_sheet('my_first_spreadsheet') #adding and renaming a column

#writing labels
newsheet.write(0,0,'number') #write in the first cel A1
newsheet.write(0,1,'square') #write in B1
newsheet.write(0,2,'is a even number?') #write in C1

#creating a list

list_numbers = list(xrange(100))

for item in list_numbers:
	newsheet.write(i,0,item) #write in column A
	i=i+1


wb.save(from_this_dir('04_formula.xls'))