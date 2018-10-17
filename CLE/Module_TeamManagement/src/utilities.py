import traceback
import requests
import json
import csv
import sys
import os
import math
import time
import base64
import datetime
from Crypto.Cipher import AES
from CLE.settings import AES_SECRET_KEY
from Module_TeamManagement.models import *
from selenium import webdriver


#-----------------------------------------------------------------------------#
#-------------------------- Utilities Function -------------------------------#
#-----------------------------------------------------------------------------#


# Populate relevant courses related to instructors/students from database
def populateRelevantCourses(requests,instructorEmail=None,studentEmail=None):
    courseList = {}
    courseList_updated = {}

    try:
        if instructorEmail != None:
            courseObject = Faculty.objects.get(email=instructorEmail).course_section.all()
            for course_section in courseObject:
                try:
                    courseList_updated[course_section.course.course_title].append(
                        {
                            'id':course_section.course_section_id,
                            'course_title':course_section.course.course_title,
                            'section_number':course_section.section_number,
                            'to_string':course_section.course.course_title + " " + course_section.section_number,
                        }
                    )
                except:
                    courseList_updated[course_section.course.course_title] = [
                        {
                            'id':course_section.course_section_id,
                            'course_title':course_section.course.course_title,
                            'section_number':course_section.section_number,
                            'to_string':course_section.course.course_title + " " + course_section.section_number,
                        }
                    ]

        elif studentEmail != None:
            classObject = Class.objects.all().filter(student=studentEmail).distinct()
            for individuaClass in classObject:
                course_section = individuaClass.course_section
                courseList[course_section.course_section_id] = {"courseDetails" : course_section.course.course_title + " " + course_section.section_number}
                toolsList=[]
                try:
                    currentCourseTools = course_section.learning_tools.split("_")
                    for tools in currentCourseTools:
                        if tools not in toolsList:
                            toolsList.append(tools)
                except:
                    pass
                courseList[course_section.course_section_id]["toolImage_list"] = toolsList
                try:
                    courseList_updated[course_section.course.course_title].update(
                        {
                            'id':course_section.course_section_id,
                            'course_title':course_section.course.course_title,
                            'section_number':course_section.section_number,
                            'to_string':course_section.course.course_title + " " + course_section.section_number,
                        }
                    )
                except:
                    courseList_updated[course_section.course.course_title] = {
                        'id':course_section.course_section_id,
                        'course_title':course_section.course.course_title,
                        'section_number':course_section.section_number,
                        'to_string':course_section.course.course_title + " " + course_section.section_number,
                    }


    except :
        traceback.print_exc()

    requests.session['courseList'] = courseList
    requests.session['courseList_updated'] = courseList_updated
    return

# Returns all trailhead webscrapper info from tcsv():
#
# final format should be
# results = {
#     "joel.tay.2016@smu.edu.sg" : {'badge_count' : 4 , ...}
#     "shlye.2016@smu.edu.sg" :{'badge_count': '52', 'points_count': '29,650', 'trail_count': '3', 'badges_obtained': ['commerce_cloud_functional_consulting', .. }
# }
#
def getTrailheadInformation():
    file_path = os.path.join(os.getcwd(),'clt_files','trailhead-points.csv')
    results ={}

    with open(file_path,mode='r',encoding='cp1252') as csvInput:
        csv_reader = csv.reader(csvInput, delimiter=',')
        counter = 0

        for row in csv_reader:
            content = {}

            if counter == 0:
                results['last_updated'] = row[1] # take last updated information
                counter+=1
            elif counter ==1:
                counter+=1
                pass #skip headers
            else:

                # Track all student information
                studId = row[1]
                content['badge_count'] = row[3]
                content['points_count'] = row[4]
                content['trail_count'] = row[5]

                badges_obtained = row[6].split('|')
                new_badges_obtained = []
                for badge_obtained in badges_obtained:
                    new_badges_obtained.append(badge_obtained.replace(" ","_").lower())

                content['badges_obtained'] = new_badges_obtained
                results[studId] = content #Key is student_email
    return results


# Main method to retreive all information of trailhead informations
#
# final format should be
# context = {
#     "personal" : {'badge_count' : 4 , ...} # dependent on student if not will be missing
#     "CourseTrailResults" : {'badge_count' : 4 , ...}
# }
#
def populateTrailheadInformation(requests, student_email=None, instructorEmail=None):
    context = {}
    trailHeadInfo = getTrailheadInformation()

    if requests.method == 'GET':
        moduleCode = requests.GET.get('module')
    else:
        moduleCode = requests.POST.get('course_section')

    if student_email != None:
        try:
            context["personal"] = trailHeadInfo[student_email]
        except:
            context["personal"] = {'badge_count':0,'points_count':0,'trail_count':0, 'badges_obtained':[]}
        try:
            context["CourseTrailResults"] = populateTeamTrailHeadInformation(trailHeadInfo,studentemail=student_email)
        except:
            context["CourseTrailResults"] = {"class" : {"Teams_Information": {}, "Students_Information": {"students" :[] , "points" : [] , "badges": []}}}

    if instructorEmail != None:
        if moduleCode != None:
            context["CourseTrailResults"] = populateTeamTrailHeadInformation(trailHeadInfo,courseSection=moduleCode) #for selective course modules titles
        else:
            context["CourseTrailResults"] = populateTeamTrailHeadInformation_instructor(trailHeadInfo,instructorEmail ) # instructor dashboard

    context["last_updated"] = trailHeadInfo["last_updated"]
    #print(context)
    return context


# Retrieve team info based on course - For instructor dashboard retrieval
#
# final format should be
# 'CourseTrailResults': {
#     BPAS210G4: {
#         "Teams_Information" : {
#             'T1': {'badges': 185, 'points': 162700, 'trails': 15}, 'T2': {'badges': 392, 'points': 288475, 'trails': 51},
#
#             'T3': {'badges': 280, 'points': 207475, 'trails': 26} ...
#         },
#         "Students_Information" : {
#             "students" : [joel.tay.2016, shlye.2016, martin.teo.2016 ...]
#             "points" : [2323, 3333, 4445 ..]
#             "badges" : [3, 5, 6...]
#         }
#
#     },
#     BPAS201G2: {
#         "Teams_Information" : {...}
#         "Students_Information" : {...}
#     }
#
# }
#
def populateTeamTrailHeadInformation_instructor(results, instructorEmail):
    facultyObj = Faculty.objects.filter(email=instructorEmail)[0]
    registered_course_section = facultyObj.course_section.all()
    courses = []

    for course_section in registered_course_section:
        courses.append(course_section.course_section_id)

    classes = Class.objects.order_by('course_section','team_number')
    classResult = {}
    for classObj in classes:
        course_section_id = classObj.course_section.course_section_id #Getting course code
        if course_section_id in courses: #extract classes only

            try:
                if course_section_id not in classResult:
                    classResult[course_section_id] = {}
                    classResult[course_section_id]["Teams_Information"] = {}
                    classResult[course_section_id]["Students_Information"] = {"students" :[] , "points" : [] , "badges": []}
                try:
                    #populate student results
                    classResult[course_section_id]["Students_Information"]["students"].append(classObj.student.email.split("@")[0])
                    student = Cloud_Learning_Tools.objects.get(id=classObj.student.email.split("@")[0]+"_TrailHead") #If there is no query, it will be zero
                    classResult[course_section_id]["Students_Information"]["badges"].append(int(results[classObj.student.email]['badge_count']))
                    classResult[course_section_id]["Students_Information"]["points"].append(int(results[classObj.student.email]['points_count'].replace(",","")))
                except:
                    pass

                if classObj.team_number != None : #Omit classes with no teams
                # populate team results
                    if classObj.team_number not in classResult[course_section_id]["Teams_Information"]:
                        classResult[course_section_id]["Teams_Information"][classObj.team_number] = {"badges": 0, "points":0, "trails":0 }
                    try:
                        student = Cloud_Learning_Tools.objects.get(id=classObj.student.email.split("@")[0]+"_TrailHead") #If there is no query, it will be zero
                        classResult[course_section_id]["Teams_Information"][classObj.team_number]["badges"] += int(results[classObj.student.email]['badge_count'])
                        classResult[course_section_id]["Teams_Information"][classObj.team_number]["points"] += int(results[classObj.student.email]['points_count'].replace(",",""))
                        classResult[course_section_id]["Teams_Information"][classObj.team_number]["trails"] += int(results[classObj.student.email]['trail_count'])
                    except:
                        pass
            except:
                pass # for cases where they dont have trail head links

    return classResult


# Retrieve team info based on course for both students main page and instructor class page - For student dashboard retrieval
#
# final format should be
# 'CourseTrailResults': {
#     "class": {
#         "Teams_Information" : {
#             'T1': {'badges': 185, 'points': 162700, 'trails': 15}, 'T2': {'badges': 392, 'points': 288475, 'trails': 51},
#             'T3': {'badges': 280, 'points': 207475, 'trails': 26} ...
#         },
#         "Students_Information" : {
#             "students" : [joel.tay.2016, shlye.2016, martin.teo.2016 ...]
#             "points" : [2323, 3333, 4445 ..]
#             "badges" : [3, 5, 6...]
#         }
#     },
#     "studentLoopTimes" : range(0, number of students)
# }

def populateTeamTrailHeadInformation(results, studentemail=None, courseSection=None):
    if courseSection == None:
        classStudentObj = Class.objects.filter(student=studentemail)
        courseSection = classStudentObj[0].course_section.course_section_id

    # SQL equivalent to filter by course section and order by team_number
    classResult = classInformationRetrieval(results, courseSection)
    classResult["studentLoopTimes"] = range(len(classResult["class"]["Students_Information"]["points"]))
    return classResult


# Retreive information from trailheadinformation of a certain course Section
#
# "class": {
#         "Teams_Information" : {
#             'T1': {'badges': 185, 'points': 162700, 'trails': 15}, 'T2': {'badges': 392, 'points': 288475, 'trails': 51},
#             'T3': {'badges': 280, 'points': 207475, 'trails': 26} ...
#         },
#         "Students_Information" : {
#             "students" : [joel.tay.2016, shlye.2016, martin.teo.2016 ...]
#             "points" : [2323, 3333, 4445 ..]
#             "badges" : [3, 5, 6...]
#         }
#
# }
#
def classInformationRetrieval(results, courseSection):
    classes = Class.objects.filter(course_section= courseSection).order_by('team_number')
    classResult = {}
    classResult["class"] = {}
    classResult["class"]["Teams_Information"] = {}
    classResult["class"]["Students_Information"] = {"students" :[] , "points" : [] , "badges": []}
    for classObj in classes:
        try:
            student = Cloud_Learning_Tools.objects.get(id=classObj.student.email.split("@")[0]+"_TrailHead") #If there is no query, it will be zero
            #populate student results
            classResult["class"]["Students_Information"]["students"].append(classObj.student.email.split("@")[0])
            classResult["class"]["Students_Information"]["badges"].append(int(results[classObj.student.email]['badge_count']))
            classResult["class"]["Students_Information"]["points"].append(int(results[classObj.student.email]['points_count'].replace(",","")))
        except:
            classResult["class"]["Students_Information"]["badges"].append(0)
            classResult["class"]["Students_Information"]["points"].append(0)
            pass

        if classObj.team_number != None : #Omit classes with no teams
        # populate team results
            if classObj.team_number not in classResult["class"]["Teams_Information"]:
                classResult["class"]["Teams_Information"][classObj.team_number] = {"badges": 0, "points":0, "trails":0 }
            try:
                student = Cloud_Learning_Tools.objects.get(id=classObj.student.email.split("@")[0]+"_TrailHead") #If there is no query, it will be zero
                classResult["class"]["Teams_Information"][classObj.team_number]["badges"] += int(results[classObj.student.email]['badge_count'])
                classResult["class"]["Teams_Information"][classObj.team_number]["points"] += int(results[classObj.student.email]['points_count'].replace(",",""))
                classResult["class"]["Teams_Information"][classObj.team_number]["trails"] += int(results[classObj.student.email]['trail_count'])
            except: 
                pass

    return classResult


# The webscrapper to scrap static info from website
def webScrapper():
    from bs4 import BeautifulSoup
    from Module_TeamManagement.models import Cloud_Learning_Tools
    import datetime
    import pytz

    output_file = 'clt_files/trailhead-points.csv'
    st = time.time()

    clt_tools = Cloud_Learning_Tools.objects.filter(type='TrailHead')

    studentEmails = []
    studentLinks = []

    for clt in clt_tools:
        studentEmails.append(clt.id.split("_")[0] + "@smu.edu.sg") #converts trailids to student emails
        studentLinks.append(clt.website_link)

    print("read link from file : %.9f " % (time.time()-st) )

    info = {}
    counter=0 #iterate in studentList
    for link in studentLinks:
        content = {}

        req = requests.get(link)
        soup = BeautifulSoup(req.text, 'html.parser')
        broth = soup.find(attrs={'data-react-class': 'BadgesPanel'})

        json_obj = json.loads(str(broth['data-react-props']))

        titles = []
        for i in json_obj['badges']:
            titles.append(i['title'])

        name = soup.find(attrs={'class', 'slds-p-left_x-large slds-size_1-of-1 slds-medium-size_3-of-4'}).find('div')
        stats = soup.find_all('div', attrs={'class', 'user-information__achievements-data'})

        content['titles'] = '|'.join(titles)
        content['name'] = json.loads(str(name['data-react-props']))['full_name']
        content['badge-count'] = stats[0].text.strip()
        content['points-count'] = stats[1].text.strip()
        content['trail-count'] = stats[2].text.strip()
        content['link'] = link

        info[studentEmails[counter]] = content #key is student email, value is information
        counter+=1

    print("scrapping info from  file : %.9f " % (time.time()-st) )

    counter = 0
    with (open(output_file, 'w', newline='', encoding='utf-8-sig')) as file:
        writer = csv.writer(file)
        tz = pytz.timezone('Asia/Singapore')
        writer.writerow(["last updated:" , str(datetime.datetime.now(tz=tz))[:19]])
        writer.writerow(['link','student_email','trailhead_name', 'badges', 'points', 'trails', 'badges_obtained'])

        for email,content in info.items():
            to_write = [
                content['link'],
                email,
                content['name'].replace("," , "").replace("_" , ""),
                content['badge-count'].replace("," , ""),
                content['points-count'].replace("," , ""),
                content['trail-count'].replace("," , ""),
                content['titles']
            ]
            writer.writerow(to_write)

    print("done scrapping info from  file : %.9f " % (time.time()-st) )


# The webscrapper to scrap static info from website - single link
def webScrapper_SingleLink(student_email,link):
    from bs4 import BeautifulSoup
    import datetime
    import pytz

    output_file = os.path.join(os.getcwd(),'clt_files','trailhead-points.csv')
    content = []

    req = requests.get(link)
    soup = BeautifulSoup(req.text, 'html.parser')
    broth = soup.find(attrs={'data-react-class': 'BadgesPanel'})

    json_obj = json.loads(str(broth['data-react-props']))

    titles = []
    for i in json_obj['badges']:
        titles.append(i['title'])

    name = soup.find(attrs={'class', 'slds-p-left_x-large slds-size_1-of-1 slds-medium-size_3-of-4'}).find('div')
    stats = soup.find_all('div', attrs={'class', 'user-information__achievements-data'})

    if os.path.isfile(output_file):
        with open(output_file, mode='r', encoding='utf-8') as inputFile:
            reader = csv.reader(inputFile, delimiter=',')
            for row in reader:
                if row[1] != student_email:
                    content.append(row)
    else:
        content = [['link','student_email','trailhead_name', 'badges', 'points', 'trails', 'badges_obtained']] + content

    content.append(
        [
            link,
            student_email,
            json.loads(str(name['data-react-props']))['full_name'].replace("," , "").replace("_" , ""),
            stats[0].text.strip().replace("," , ""),
            stats[1].text.strip().replace("," , ""),
            stats[2].text.strip().replace("," , ""),
            '|'.join(titles)
        ]
    )

    with (open(output_file, mode='w', newline='')) as outputFile:
        writer = csv.writer(outputFile)
        for row in content:
            new_row = []
            for word in row:
                new_row.append(str(word.encode('utf-8').decode('ascii', 'ignore')))
            writer.writerow(new_row)


# Encrypt a 32-bit string
# Accepts:
# - plainText : string
#
# Return:
# - cipherText : string
def encode(plainText=''):
    if plainText == '':
        raise Exception('Please specify a 32 bit long plain text when encoding')

    if len(plainText) <= 32:
        plainText = plainText.rjust(32)
        cipher = AES.new(AES_SECRET_KEY.encode('utf-8'),AES.MODE_ECB)
        return base64.b64encode(cipher.encrypt(plainText.encode('utf-8'))).strip().decode('utf-8')

    return encode(plainText[:int(len(plainText)/2)]) + encode(plainText[int(len(plainText)/2):])

# Decrypt a 32-bit string
# Accepts:
# - cipherText : string
#
# Return:
# - plainText : string
def decode(cipherText=''):
    if cipherText == '':
        raise Exception('Please specify a cipher text for decoding')

    if len(cipherText) <= 44:
        cipher = AES.new(AES_SECRET_KEY.encode('utf-8'),AES.MODE_ECB)
        return cipher.decrypt(base64.b64decode(cipherText.encode('utf-8'))).strip().decode('utf-8')

    return decode(cipherText[:44]) + decode(cipherText[44:])


# Return a string of the current financial year
def getFinancialYear():
    year = int(datetime.datetime.now().strftime("%y"))
    month = int(datetime.datetime.now().strftime("%m"))

    if month >= 4:
        fin_year = 'AY' + str(year) + '/' + str(year+1)
    else:
        fin_year = 'AY' + str(year-1) + '/' + str(year)

    return fin_year


# Returns an int of the current school term
def getSchoolTerm():
    currentMonth = int(datetime.datetime.now().strftime("%m"))

    if currentMonth >= 8 and currentMonth <= 12:
        return 1
    elif currentMonth >= 1 and currentMonth <= 4:
        return 2
    else:
        return 3


# Returns two int of the number of remaining & past weeks since school term start
def getRemainingWeeks():
    school_term_id = getFinancialYear() + 'T' + str(getSchoolTerm())
    try:
        school_termObj = School_Term.objects.get(school_term_id=school_term_id)
    except:
        return None, None

    # Calculate the difference in days
    term_start_date = school_termObj.start_date
    today = datetime.datetime.date(datetime.datetime.now())
    difference_days_start = (today - term_start_date).days

    # Calculate number of past weeks since start of school term
    past_weeks = math.ceil(difference_days_start / 7)
    remaining_weeks = 16 - past_weeks

    return past_weeks, remaining_weeks


# Validates if date string is in proper format
def validateDate(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False
