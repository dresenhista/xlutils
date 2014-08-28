import os
import sys
from xlwt import *

from base import from_this_dir

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
#to write a simple file you just need the xlwt package.


wb = Workbook() # create empty workbook object
newsheet = wb.add_sheet('my_first_spreadsheet') #adding and renaming a column

newsheet.write(0,0,'Hello') #write in the first cel A1
newsheet.write(0,1,'World!') #write in B1
newsheet.write(1,0,'I am') #write in A2
newsheet.write(1,1,'learning') #write in B2

wb.save(from_this_dir('01_simple_basic.xls'))