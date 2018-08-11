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
        # team_number = 'T' + list(filter(None,teamList))[0].split()[-1]

        # Create student : list
        # student = [email,username,firstname,lastname,team_number]
        student = [email,username,firstname,lastname]

        # Store in dict with section_number as key and student : list as value
        try:
            bootstrapInfo[section_number]['students'].append(student)
        except Exception as ex:
            if ex.args[0] == section_number:
                bootstrapInfo[section_number] = {'students':[student]}
            elif ex.args[0] == 'student':
                bootstrapInfo[section_number].update({'students':[student]})

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
    # index_hp = headers.index('Phone Number')

    # Start with '1' instead of '0' to clear header buffer
    for row in range(1,sheet.nrows):
        rowData = sheet.row_values(row)

        # Declare variables
        username = rowData[index_username].strip()
        if '\\' in username:
            username = username.split("\\")[1]

        email = rowData[index_email].strip()
        firstname = rowData[index_firstname].strip()
        lastname = rowData[index_lastname].strip()

        # phoneNumber = str(int(rowData[index_hp])).strip()
        # if len(phoneNumber) == 8:
        #     phoneNumber = str('65') + phoneNumber
        # elif '+' in phoneNumber and len(phoneNumber) == 11:
        #     phoneNumber = phoneNumber[1:]

        # Create faculty : list
        # faculty = [email,username,firstname,lastname,phoneNumber]
        faculty = [email,username,firstname,lastname]

        # Store in dict with faculty as key and faculty : list as value
        try:
            bootstrapInfo['faculty'].append(faculty)
        except:
            bootstrapInfo['faculty'] = [faculty]

    return bootstrapInfo


def parse_File_Course(filePath,bootstrapInfo={}):

    # Create a workbook object from the classFile
    workbook = xlrd.open_workbook(filePath)

    # Get first worksheet
    sheet = workbook.sheet_by_index(0)

    # Get headers
    headers = sheet.row_values(0)

    # Get header indexes of each column
    index_title = headers.index('Title')
    index_name = headers.index('Name')
    index_desc = headers.index('Description')

    # Start with '1' instead of '0' to clear header buffer
    for row in range(1,sheet.nrows):
        rowData = sheet.row_values(row)

        # Declare variables
        course_Title = rowData[index_title].strip()
        course_Name = rowData[index_name].strip()
        course_Desc = rowData[index_desc].strip()

        # Create course : list
        course = [course_Title,course_Name,course_Desc]

        # Store in dict with course as key and course : list as value
        try:
            bootstrapInfo['course'].append(course)
        except:
            bootstrapInfo['course'] = [course]

    return bootstrapInfo


def parse_File_CLT(filePath,bootstrapInfo={}):
    # TO-DO
    return bootstrapInfo


def bootstrap_Faculty(fileDict):
    bootstrapInfo = {}
    results = {}

    if fileDict['file_type'] == 'zip':
        bootstrapInfo = parse_File_Faculty(fileDict['faculty'], bootstrapInfo)
        bootstrapInfo = parse_File_Course(fileDict['course'], bootstrapInfo)
        Course.objects.all().delete()
        Faculty.objects.all().delete()

    elif fileDict['file_type'] == 'excel' and fileDict['file_information'] == 'course':
        bootstrapInfo = parse_File_Course(fileDict['file_path'], bootstrapInfo)
        Course.objects.all().delete()

    elif fileDict['file_type'] == 'excel' and fileDict['file_information'] == 'faculty':
        bootstrapInfo = parse_File_Faculty(fileDict['file_path'], bootstrapInfo)
        Faculty.objects.all().delete()

    try:
        for user,data in bootstrapInfo.items():
            if user == 'course':
                results['course_count'] = len(data)
                for course in data:
                    try:
                        Course.objects.get(course_title=course[0])
                    except:
                        courseObj = Course.objects.create(
                            course_title=course[0],
                            course_name=course[1],
                            course_description=course[2],
                        )
                        courseObj.save()
            else:
                results['faculty_count'] = len(data)
                for faculty in data:
                    try:
                        Faculty.objects.get(email=faculty[0])
                    except:
                        facultyObj = Faculty.objects.create(
                            email=faculty[0],
                            username=faculty[1],
                            firstname=faculty[2],
                            lastname=faculty[3],
                            # phone_number=faculty[4],
                        )
                        facultyObj.save()

    except Exception as e:
        # Uncomment for debugging - to print stack trace wihtout halting the process
        traceback.print_exc()
        raise Exception('Unsuccessful Upload')

    return results


def bootstrap_Students(fileDict):
    bootstrapInfo = {}
    results = {}

    bootstrapInfo = parse_File_Student(fileDict['file_path'],bootstrapInfo)

    course_title = fileDict['course_title']
    faculty_username = fileDict['faculty_username']

    facultyObj = Faculty.objects.get(username=faculty_username)
    courseObj = Course.objects.get(course_title=course_title)

    # Clear info from database =================================================
    try:
        section_numbers = bootstrapInfo.keys()
        course_section_ids = [course_title + section_number for section_number in section_numbers]

        for course_section_id in course_section_ids:
            if Class.objects.all().filter(course_section=course_section_id).exists():
                Class.objects.all().filter(course_section=course_section_id).delete()
            if Course_Section.objects.all().filter(course_section_id=course_section_id).exists():
                course_sectionObj = Course_Section.objects.get(course_section_id=course_section_id)
                facultyObj.course_section.remove(course_sectionObj)
                course_sectionObj.delete()

    except Exception as e:
        # Uncomment for debugging - to print stack trace wihtout halting the process
        traceback.print_exc()
        raise Exception('Unsuccessful Upload')
    # ==========================================================================


    # Bootstrap info into database =============================================
    try:
        student_count = 0
        for section_number,section_Data in bootstrapInfo.items():
            try:
                course_sectionObj = Course_Section.objects.get(course_section_id=course_title+section_number)
            except:
                course_sectionObj = Course_Section.objects.create(
                    course_section_id=course_title+section_number,
                    course=courseObj,
                    section_number=section_number,
                )
                course_sectionObj.save()

            facultyObj.course_section.add(course_sectionObj)

            for user,data in section_Data.items():
                if user == 'students':
                    student_count += len(data)
                    for student in data:
                        try:
                            studentObj = Student.objects.get(email=student[0])
                        except:
                            studentObj = Student.objects.create(
                                email=student[0],
                                username=student[1],
                                firstname=student[2],
                                lastname=student[3],
                            )
                            studentObj.save()

                        try:
                            Class.obects.get(student=studentObj)
                        except:
                            classObj = Class.objects.create(
                                student=studentObj,
                                course_section=course_sectionObj,
                            )
                            classObj.save()

        results['section_count'] = len(bootstrapInfo)
        results['student_count'] = student_count

    except Exception as e:
        # Uncomment for debugging - to print stack trace wihtout halting the process
        traceback.print_exc()
        raise Exception('Unsuccessful Upload')
    # ==========================================================================

    return results
