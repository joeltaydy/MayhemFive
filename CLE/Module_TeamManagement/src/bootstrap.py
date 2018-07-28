import xlrd
from django.core.files import File
from Module_TeamManagement.models import Section, Student, Instructor, Assigned_Team, Teaching_Assistant

#-----------------------------------------------------------------------------#
#-------------------------- Bootstrap Function -------------------------------#
#-----------------------------------------------------------------------------#

def parse_Excel_Student(file,courseInfo={}):

    # Create a workbook object from the file
    workbook = xlrd.open_workbook(file.temporary_file_path())

    # Get first worksheet
    sheet = workbook.sheet_by_index(0)

    # Get headers
    headers = sheet.row_values(0)

    # Get header indexes of each column
    index_username = headers.index('Username')
    index_lastname = headers.index('Last Name')
    index_firstname = headers.index('First Name')
    index_email = headers.index('Email')
    index_section = headers.index('Section')

    # Start with '1' instead of '0' to clear header buffer
    for row in range(1,sheet.nrows):
        rowData = sheet.row_values(row)
        teamList = rowData[index_section+1:]

        # Declare variables
        username = rowData[index_username].strip()
        if '\\' in username:
            username = username.split("\\")[1]

        section_number = rowData[index_section].strip()
        if ',' in section_number:
            section_number = section_number.split(",")[1]

        email = rowData[index_email].strip()
        firstname = rowData[index_firstname].strip()
        lastname = rowData[index_lastname].strip()
        team_number = 'T' + list(filter(None,teamList))[0].split()[-1]

        # Create student : list
        student = [email,username,firstname,lastname,team_number]

        # Store in dict with section_number as key and student : list as value
        try:
            courseInfo[section_number]['student'].append(student)
        except Exception as ex:
            if ex.args[0] == section_number:
                courseInfo[section_number] = {'student':[student]}
            elif ex.args[0] == 'student':
                courseInfo[section_number].update({'student':[student]})

    return courseInfo


def parse_Excel_Instructor(file,courseInfo={}):

    # Create a workbook object from the file
    workbook = xlrd.open_workbook(file.temporary_file_path())

    # Get first worksheet
    sheet = workbook.sheet_by_index(0)

    # Get headers
    headers = sheet.row_values(0)

    # Get header indexes of each column
    index_username = headers.index('Username')
    index_lastname = headers.index('Last Name')
    index_firstname = headers.index('First Name')
    index_email = headers.index('Email')
    index_hp = headers.index('Phone Number')
    index_section = headers.index('Section') # Assume that there are more than one section and they are seperated by commas

    # Start with '1' instead of '0' to clear header buffer
    for row in range(1,sheet.nrows):
        rowData = sheet.row_values(row)

        # Declare variables
        username = rowData[index_username].strip()
        if '\\' in username:
            username = username.split("\\")[1]

        section_number_list = rowData[index_section].strip().split(",")
        email = rowData[index_email].strip()
        firstname = rowData[index_firstname].strip()
        lastname = rowData[index_lastname].strip()

        phoneNumber = rowData[index_hp].strip()
        if len(phoneNumber) == 8:
            phoneNumber = str('65') + phoneNumber
        elif '+' in phoneNumber and len(phoneNumber) == 11:
            phoneNumber = phoneNumber[1:]

        # Create instructor : list
        instructor = [email,username,firstname,lastname,phoneNumber]

        # Store in dict with section_number as key and instructor : list as value
        for section_number in section_number_list:
            try:
                courseInfo[section_number]['instructor'].append(instructor)
            except Exception as ex:
                if ex.args[0] == section_number:
                    courseInfo[section_number] = {'instructor':[instructor]}
                elif ex.args[0] == 'instructor':
                    courseInfo[section_number].update({'instructor':[instructor]})

    return courseInfo


def parse_Excel_Assistant(file,courseInfo={}):

    # Create a workbook object from the classFile
    workbook = xlrd.open_workbook(file.temporary_file_path())

    # Get first worksheet
    sheet = workbook.sheet_by_index(0)

    # Get headers
    headers = sheet.row_values(0)

    # Get header indexes of each column
    index_username = headers.index('Username')
    index_lastname = headers.index('Last Name')
    index_firstname = headers.index('First Name')
    index_email = headers.index('Email')
    index_section = headers.index('Section')

    # Start with '1' instead of '0' to clear header buffer
    for row in range(1,sheet.nrows):
        rowData = sheet.row_values(row)

        # Declare variables
        username = rowData[index_username].strip()
        if '\\' in username:
            username = username.split("\\")[1]

        section_number = rowData[index_section].strip()
        if ',' in section_number:
            section_number = section_number.split(',')[-1]

        email = rowData[index_email].strip()
        firstname = rowData[index_firstname].strip()
        lastname = rowData[index_lastname].strip()

        # Create teaching_assistant : list
        teaching_assistant = [email,username,firstname,lastname]

        # Store in dict with section_number as key and teaching_assistant : list as value
        try:
            courseInfo[section_number]['teaching_assistant'].append(teaching_assistant)
        except Exception as ex:
            if ex.args[0] == section_number:
                courseInfo[section_number] = {'teaching_assistant':[teaching_assistant]}
            elif ex.args[0] == 'teaching_assistant':
                courseInfo[section_number].update({'teaching_assistant':[teaching_assistant]})

    return courseInfo


def clear_Database():
    Section.objects.all().delete()
    Student.objects.all().delete()
    Assigned_Team.objects.all().delete()
    Instructor.objects.all().delete()
    Teaching_Assistant.objects.all().delete()


# TO-DO: Reconfigure model to accept this format; Currently not configured to accept Teaching_Assistant Model
# Format of dictionary:
# Section
#   |- Student
#       |- [email,username,firstname,lastname]
#       |- [email,username,firstname,lastname]
#       |- [email,username,firstname,lastname]
#       |- ...
#   |- Instructor
#       |- [email,username,firstname,lastname,section]
#       |- [email,username,firstname,lastname,section]
#       |- [email,username,firstname,lastname,section]
#       |- ...
#   |- Teaching_Assistant
#       |- [email,username,firstname,lastname,section]
#       |- [email,username,firstname,lastname,section]
#       |- [email,username,firstname,lastname,section]
#       |- ...
#
def bootstrap(fileDict):
    if fileDict['type'] == 'excel':
        courseInfo = parse_Excel_Student(fileDict['file']) if fileDict['user'] == 'student' else parse_Excel_Instructor(fileDict['file'])
    else:
        try:
            courseInfo = parse_Excel_Student(fileDict['file_student'])
            courseInfo = parse_Excel_Instructor(fileDict['file_instructor'],courseInfo)
        except:
            raise Exception(".zip file does not contain the required excel files.")
        clear_Database()

    # Bootstrap data into database
    for section,sectionData in courseInfo.iteritems():
        sectionObj = Section.objects.create(section_number=section)

        for userType,data in sectionData.iteritems():
            if userType == 'student':
                studentList = courseInfo[section]['student']

                for student in studentList:
                    studentObj = Student.objects.create(
                        email=student[0],
                        username=student[1],
                        firstname=student[2],
                        lastname=student[3],
                    )

                    team = Assigned_Team.objects.create(
                        student=studentObj,
                        team_number=student[5],
                        section=sectionObj,
                    )

                    studentObj.save()
                    team.save()

            elif userType == 'instructor':
                instructorList = courseInfo[section]['instructor']

                for instructor in instructorList:
                    instructorObj = Instructor.objects.create(
                        email=instructor[0],
                        username=instructor[1],
                        firstname=instructor[2],
                        lastname=instructor[3],
                        phone_number=instructor[4],
                        section=sectionObj,
                    )

                    instructorObj.save()
