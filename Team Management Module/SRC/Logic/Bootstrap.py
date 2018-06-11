import xlrd
import time
import csv

classFile = "../../SampleData/SampleData2_Class_Roster.xlsx"


workbook = xlrd.open_workbook(classFile)
sheet = workbook.sheet_by_index(0) #first worksheet

header = sheet.row_values(0) # header 
#print header

studentData = []

for rowx in xrange(1,sheet.nrows): # clear header buffer
    rowData = sheet.row_values(rowx)
    studentParticulars = [] # each student information in this format [EMAIL, USERNAME, FIRST NAME, LAST NAME, PASSWORD, SECT NO, TEAM NO]
    # Row data is in this format [u'Username', u'Last Name', u'First Name', u'Email', u'Section', u'Project G1', u'Project G2', u'Project G3', u'Project G4', u'Project G5', u'Project G6', u'Project G7']
    studentParticulars.extend([rowData[3],rowData[0],rowData[2],rowData[1]])
    
    # default password can be changed here 
    password = rowData[0].upper()+rowData[2].lower()+"_ESM1001"
    #print password
    studentParticulars.append(password)
    
    #Section and team information
    newList = list(filter(None,rowData[5:]))
    sectionTeam = [newList[0][:3],newList[0][3:]]
    studentParticulars.extend(sectionTeam)
    
    studentData.append(studentParticulars)

with open('../../SampleData/studentProcessed.csv','wb') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerow(["EMAIL", "USERNAME", "FIRST NAME", "LAST NAME", "PASSWORD", "SECT NO"," TEAM NO"])
    for row in studentData:
        writer.writerow(row)
print "done"
