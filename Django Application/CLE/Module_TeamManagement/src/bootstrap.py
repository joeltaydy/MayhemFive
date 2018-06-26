import xlrd
from django.core.files import File
from Module_TeamManagement.models import Section, Student, Instructor, Assigned_Team

#-----------------------------------------------------------------------------#
#-------------------------- Bootstrap Function -------------------------------#
#-----------------------------------------------------------------------------#

def parse_Excel(classFile):
    teamManagementDict = {}

    # Create a workbook object from the classFile
    workbook = xlrd.open_workbook(classFile.temporary_file_path())

    # Get first worksheet
    sheet = workbook.sheet_by_index(0)

    # Start with '1' instead of '0' to clear header buffer
    for rowx in xrange(1,sheet.nrows):

        # Row data is in this format:
        # ['Email' , u'Username', u'Last Name', u'First Name', u'Email', u'Section', u'Project G1', u'Project G2', u'Project G3', u'Project G4', u'Project G5', u'Project G6', u'Project G7']
        rowData = sheet.row_values(rowx)
        newList = list(filter(None,rowData[5:]))

        # Declare variables
        username = rowData[0]
        if "smustu\\" in username:
            username = username.split("\\")[1]

        email = rowData[3]
        firstname = rowData[2]
        lastname = rowData[1]
        password = "temp12345"
        section_number = newList[0][:3]
        team_number = newList[0][3:]

        # Create student : list
        student = [email,username,firstname,lastname,password,team_number]

        # Store in dict with section_number as key and student : list as value
        if section_number not in teamManagementDict.keys():
            teamManagementDict[section_number] = [student]
        else:
            teamManagementDict[section_number].append(student)

    return teamManagementDict

def clearDB():
    Section.objects.all().delete()
    Student.objects.all().delete()
    Assigned_Team.objects.all().delete()

def bootstrap(classFile):
    clearDB()
    teamManagementDict = parse_Excel(classFile)

    # Bootstrap data into database
    for section in teamManagementDict.keys():
        sectionObj = Section.objects.create(section_number=section)
        studentList = teamManagementDict[section]

        for student in studentList:
            studentObj = Student.objects.create(
                email=student[0],
                username=student[1],
                firstname=student[2],
                lastname=student[3],
                password=student[4],
            )
            print(student[5])
            team = Assigned_Team.objects.create(
                student=studentObj,
                team_number=student[5],
                section=sectionObj,
            )

            team.save()
