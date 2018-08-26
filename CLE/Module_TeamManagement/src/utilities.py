import traceback
import requests
import json
import csv
import sys
import os
import time
from Module_TeamManagement.models import Cloud_Learning_Tools,Faculty,Class


#-----------------------------------------------------------------------------#
#-------------------------- Utilities Function -------------------------------#
#-----------------------------------------------------------------------------#


# Populate relevant courses related to instructors/students from database
def populateRelevantCourses(requests,instructorEmail=None,studentEmail=None):
    courseList = {}
    try:
        if instructorEmail != None:
            courseObject = Faculty.objects.get(email=instructorEmail).course_section.all()
            for course in courseObject:
                courseList[course.course_section_id] = course.course.course_title + " " + course.section_number

        elif studentEmail != None:
            classObject = Class.objects.all().filter(student=studentEmail).distinct()
            for individuaClass in classObject:
                course_section = individuaClass.course_section
                courseList[course_section.course_section_id] = course_section.course.course_title + " " + course_section.section_number
    except :
        traceback.print_exc()

    requests.session['courseList'] = courseList
    return

# Returns all trailhead webscrapper info from tcsv():
'''
        final format should be
        results = {
            "joel.tay.2016@smu.edu.sg" : {'badge_count' : 4 , ...}
            "shlye.2016@smu.edu.sg" :{'badge_count': '52', 'points_count': '29,650', 'trail_count': '3', 'badges_obtained': ['commerce_cloud_functional_consulting', .. }
        }

'''
def getTrailheadInformation():
    file_path = os.path.join(os.getcwd(),'clt_files','trailhead-points.csv')
    results ={}

    with open(file_path,mode='r',encoding='cp1252') as csvInput:
        csv_reader = csv.reader(csvInput, delimiter=',')
        counter = 0

        for row in csv_reader:
            content = {}

            if counter == 0:
                results['last_updated'] = row[0] # take last updated information
                counter += 2 # skip headers
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
'''
        final format should be
        context = {
            "personal" : {'badge_count' : 4 , ...} #dependent on student if not will be missing
            "CourseTrailResults" : {'badge_count' : 4 , ...}
        }
'''
def populateTrailheadInformation(student_email=None):
    context = {}
    trailHeadInfo = getTrailheadInformation()

    if student_email != None:
        try:
            context["personal"] = trailHeadInfo[student_email]
        except:
            context["personal"] = {'badge_count':0,'points_count':0,'trail_count':0, 'badges_obtained':[]}

        context["CourseTrailResults"] = populateTeamTrailHeadInformation(trailHeadInfo,student_email)
    context["last_updated"] = trailHeadInfo["last_updated"]
    return context

# Retrieve team info based on course
'''
    final format should be
    'CourseTrailResults': {
        BPAS210G4: {
            "Teams_Information" : {
                'T1': {'badges': 185, 'points': 162700, 'trails': 15}, 'T2': {'badges': 392, 'points': 288475, 'trails': 51},
                'T3': {'badges': 280, 'points': 207475, 'trails': 26} ...            
            }, 
            "Students_Information" : {
                "students" : [joel.tay.2016, shlye.2016, martin.teo.2016 ...]
                "points" : [2323, 3333, 4445 ..]
                "badges" : [3, 5, 6...]
            }
            
        },
        BPAS201G2: {
            "Teams_Information" : {...}
            "Students_Information" : {...}
        }

    }
'''
def populateTeamTrailHeadInformation(results): #This is for instructor retrieval
    # SQL equivalent to order by course_section , team_number
    classes = Class.objects.order_by('course_section','team_number')
    

    classResult = {}
    for classObj in classes:
        course_section_id = classObj.course_section.course_section_id #Getting course code 
        if course_section_id not in classResult:
            classResult[course_section_id] = {}
            classResult[course_section_id]["Teams_Information"] = {}
            classResult[course_section_id]["Students_Information"] = {"students" :[] , "points" : [] , "badges": []}
        try:
            #populate student results
            classResult[course_section_id]["Students_Information"]["students"].append(classObj.student.email.split("@")[0])
            classResult[course_section_id]["Students_Information"]["badges"].append(int(results[classObj.student.email]['badge_count']))
            classResult[course_section_id]["Students_Information"]["points"].append(int(results[classObj.student.email]['points_count'].replace(",","")))
        except: 
            pass

        if classObj.team_number != None : #Omit classes with no teams
        # populate team results
            if classObj.team_number not in classResult[course_section_id]["Teams_Information"]:
                classResult[course_section_id]["Teams_Information"][classObj.team_number] = {"badges": 0, "points":0, "trails":0 }
            classResult[course_section_id]["Teams_Information"][classObj.team_number]["badges"] += int(results[classObj.student.email]['badge_count'])
            classResult[course_section_id]["Teams_Information"][classObj.team_number]["points"] += int(results[classObj.student.email]['points_count'].replace(",",""))
            classResult[course_section_id]["Teams_Information"][classObj.team_number]["trails"] += int(results[classObj.student.email]['trail_count'])

    return classResult

# Retrieve team info based on course
'''
    final format should be
    'CourseTrailResults': {
        BPAS210G4: {
            "Teams_Information" : {
                'T1': {'badges': 185, 'points': 162700, 'trails': 15}, 'T2': {'badges': 392, 'points': 288475, 'trails': 51},
                'T3': {'badges': 280, 'points': 207475, 'trails': 26} ...            
            }, 
            "Students_Information" : {
                "students" : [joel.tay.2016, shlye.2016, martin.teo.2016 ...]
                "points" : [2323, 3333, 4445 ..]
                "badges" : [3, 5, 6...]
            }
            
        },
        BPAS201G2: {
            "Teams_Information" : {...}
            "Students_Information" : {...}
        }

    }
'''
def populateTeamTrailHeadInformation(results, studentemail): #This is for student retrieval
    
    classStudentObj = Class.objects.filter(student=studentemail)
    courseSection = classStudentObj[0].course_section.course_section_id
    # SQL equivalent to filter by course section and order by team_number
    classes = Class.objects.filter(course_section= courseSection).order_by('team_number')
    
    classResult = {}
    classResult["class"] = {}
    classResult["class"]["Teams_Information"] = {}
    classResult["class"]["Students_Information"] = {"students" :[] , "points" : [] , "badges": []}
        
    for classObj in classes:
        try:
            #populate student results
            classResult["class"]["Students_Information"]["students"].append(classObj.student.email.split("@")[0])
            classResult["class"]["Students_Information"]["badges"].append(int(results[classObj.student.email]['badge_count']))
            classResult["class"]["Students_Information"]["points"].append(int(results[classObj.student.email]['points_count'].replace(",","")))
        except: 
            pass

        if classObj.team_number != None : #Omit classes with no teams
        # populate team results
            if classObj.team_number not in classResult["class"]["Teams_Information"]:
                classResult["class"]["Teams_Information"][classObj.team_number] = {"badges": 0, "points":0, "trails":0 }
            classResult["class"]["Teams_Information"][classObj.team_number]["badges"] += int(results[classObj.student.email]['badge_count'])
            classResult["class"]["Teams_Information"][classObj.team_number]["points"] += int(results[classObj.student.email]['points_count'].replace(",",""))
            classResult["class"]["Teams_Information"][classObj.team_number]["trails"] += int(results[classObj.student.email]['trail_count'])
    classResult["studentLoopTimes"] = range(len(classResult["class"]["Students_Information"]["points"]))
    return classResult

# The webscreapper to scrap static info from website
def webScrapper():
    from bs4 import BeautifulSoup
    from Module_TeamManagement.models import Cloud_Learning_Tools
    import datetime

    output_file = 'clt_files/trailhead-points.csv'
    st = time.time()

    clt_tools = Cloud_Learning_Tools.objects.filter(type='TrailHead')

    studentEmails = []
    studentLinks = []

    for clt in clt_tools:
        studentEmails.append(clt.id.split("_")[0] + "@smu.edu.sg") #converts trailids to student emails
        studentLinks.append(clt.website_link)

    # Removes headers
    print("read link from file : %.9f " % (time.time()-st) )
    info = {}
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

        content['titles'] = titles
        content['name'] = json.loads(str(name['data-react-props']))['full_name']
        content['badge-count'] = stats[0].text.strip()
        content['points-count'] = stats[1].text.strip()
        content['trail-count'] = stats[2].text.strip()

        info[link] = content

    print("scrapping info from  file : %.9f " % (time.time()-st) )

    counter=0 #iterate in studentList
    with (open(output_file, 'w', newline='')) as file:
        writer = csv.writer(file)
        writer.writerow(["last updated:" , str(datetime.datetime.now())])
        writer.writerow(['link','student_email','trailhead_name', 'badges', 'points', 'trails', 'badges_obtained'])
        for link,content in info.items():
            to_write = [link,studentEmails[counter], content['name'], content['badge-count'], content['points-count'], content['trail-count'], '|'.join(content['titles'])]
            writer.writerow(to_write)
            counter+=1

    print("done scrapping info from  file : %.9f " % (time.time()-st) )
