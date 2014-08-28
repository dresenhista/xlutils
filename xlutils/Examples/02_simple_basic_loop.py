import os
import sys
from xlwt import *

from base import from_this_dir

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
#to write a simple file you just need the xlwt package.


#################################################################################
#in this file we are going to write 2 spreadsheets using a loop to pupolate data#
#################################################################################

#function to populate columns
def populating_column(list_of_items, newsheet):

	i=0
	for item in list_of_items:
		newsheet.write(0,i,item)
		i=i+1

#function to populate rows
def populating_row(list_of_items, newsheet):

	j=0
	for item in list_of_items:
		newsheet.write(j,0,item)
		j=j+1


#creating excel file
wb = Workbook() # create empty workbook object
my_list = ['First column', 'Second Column', 'Third Column', 'Fourth Column']#creating a list

newsheet = wb.add_sheet('my_first_spreadsheet') #adding and renaming a column
populating_column(my_list, newsheet)

second_spreadsheet = wb.add_sheet('my_second_spreadsheet') #adding and renaming a column
populating_row(my_list, second_spreadsheet)

wb.save(from_this_dir('02_simple_basic_loop.xls'))