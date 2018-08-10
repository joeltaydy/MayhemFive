import xlrd
import time
import traceback
from django.core.files import File
from Module_TeamManagement.models import Student, Faculty, Class, Course_Section, Course, Cloud_Learning_Tools

#-----------------------------------------------------------------------------#
#-------------------------- Bootstrap Function -------------------------------#
#-----------------------------------------------------------------------------#

def parse_File_Student(filePath,bootstrapInfo={}):

    # Create a workbook object from the filePath
    workbook = xlrd.open_workbook(filePath)

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

        phoneNumber = str(int(rowData[index_hp])).strip()
        if len(phoneNumber) == 8:
            phoneNumber = str('65') + phoneNumber
        elif '+' in phoneNumber and len(phoneNumber) == 11:
            phoneNumber = phoneNumber[1:]

        # Create student : list
        student = [email,username,firstname,lastname,team_number,phoneNumber]

        # Store in dict with section_number as key and student : list as value
        try:
            bootstrapInfo[section_number]['student'].append(student)
        except Exception as ex:
            if ex.args[0] == section_number:
                bootstrapInfo[section_number] = {'student':[student]}
            elif ex.args[0] == 'student':
                bootstrapInfo[section_number].update({'student':[student]})

    return bootstrapInfo


def parse_File_Faculty(filePath,bootstrapInfo={}):

    # Create a workbook object from the filePath
    workbook = xlrd.open_workbook(filePath)

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

        phoneNumber = str(int(rowData[index_hp])).strip()
        if len(phoneNumber) == 8:
            phoneNumber = str('65') + phoneNumber
        elif '+' in phoneNumber and len(phoneNumber) == 11:
            phoneNumber = phoneNumber[1:]

        # Create instructor : list
        instructor = [email,username,firstname,lastname,phoneNumber]

        # Store in dict with section_number as key and instructor : list as value
        for section_number in section_number_list:
            try:
                bootstrapInfo[section_number]['instructor'].append(instructor)
            except Exception as ex:
                if ex.args[0] == section_number:
                    bootstrapInfo[section_number] = {'instructor':[instructor]}
                elif ex.args[0] == 'instructor':
                    bootstrapInfo[section_number].update({'instructor':[instructor]})

    return bootstrapInfo


def parse_File_Course(filePath,bootstrapInfo={}):

    # Create a workbook object from the classFile
    workbook = xlrd.open_workbook(filePath)

    # Get first worksheet
    sheet = workbook.sheet_by_index(0)

    # Get headers
    headers = sheet.row_values(0)

    # Get header indexes of each column
    index_title = headers.index('Course Title')
    index_name = headers.index('Course Name')
    index_desc = headers.index('Course Description')

    # Start with '1' instead of '0' to clear header buffer
    for row in range(1,sheet.nrows):
        rowData = sheet.row_values(row)

        # Declare variables
        course_Title = rowData[index_title].strip()
        course_Name = rowData[index_name].strip()
        course_Desc = rowData[index_desc].strip()

    return bootstrapInfo


def parse_File_CLT(filePath,bootstrapInfo={}):
    return bootstrapInfo


def clear_Database():
    Class.objects.all().delete()
    Cloud_Learning_Tools.objects.all().delete()
    Faculty.objects.all().delete()
    Course_Section.objects.all().delete()
    Student.objects.all().delete()
    Course.objects.all().delete()


def bootstrap(fileDict):
    bootstrapInfo = {}

    if fileDict['file_type'] == 'zip':
        for key in fileDict.keys():
            if 'faculty' in key:
                bootstrapInfo = parse_File_Faculty(fileDict['faculty'],bootstrapInfo)
            elif 'course' in key:
                bootstrapInfo = parse_File_Course(fileDict['course'],bootstrapInfo)
            else:
                # To-do bootstrap zip files for faculty uploads
                # bootstrapInfo = parse_File_Student(fileDict['file_path'],bootstrapInfo)
                # bootstrapInfo = parse_File_CLT(fileDict['file_path'],bootstrapInfo)

    # if fileDict['file_type'] is csv or excel
    else:


    try:
        # Bootstrap data into database
        for section,sectionData in bootstrapInfo.items():
            sectionObj = Section.objects.create(section_number=section)
            sectionObj.save()

            for userType,data in sectionData.items():
                if userType == 'student':
                    for student in data:
                        try:
                            studentObj = Student.objects.get(email=student[0])
                        except:
                            studentObj = Student.objects.create(
                                email=student[0],
                                username=student[1],
                                firstname=student[2],
                                lastname=student[3],
                                phone_number=student[5],
                            )
                            studentObj.save()

                            teamObj = Assigned_Team.objects.create(
                                student=studentObj,
                                team_number=student[4],
                                section=sectionObj,
                            )
                            teamObj.save()

                elif userType == 'teaching_assistant':
                    for assistant in data:
                        try:
                            assistanObj = Teaching_Assistant.objects.get(email=assistant[0])
                        except:
                            assistanObj = Teaching_Assistant.objects.create(
                                email=assistant[0],
                                username=assistant[1],
                                firstname=assistant[2],
                                lastname=assistant[3],
                                phone_number=assistant[4],
                                section=sectionObj,
                            )
                            assistanObj.save()

                elif userType == 'instructor':
                    for instructor in data:
                        try:
                            instructorObj = Instructor.objects.get(email=instructor[0])
                        except:
                            instructorObj = Instructor.objects.create(
                                email=instructor[0],
                                username=instructor[1],
                                firstname=instructor[2],
                                lastname=instructor[3],
                                phone_number=instructor[4],
                            )
                            instructorObj.save()

                        instructorObj.section.add(sectionObj)

    except Exception as e:
        # Uncomment for debugging - to print stack trace wihtout halting the process
        traceback.print_exc()
        # raise Exception('Unsucccessfull Upload.')
