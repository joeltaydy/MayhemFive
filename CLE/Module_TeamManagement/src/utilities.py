import traceback
import requests
import json
import csv
import sys
import os
import time
#-----------------------------------------------------------------------------#
#-------------------------- Utilities Function -------------------------------#
#-----------------------------------------------------------------------------#


# Populate relevant courses related to instructors/students from database
def populateRelevantCourses(requests,instructorEmail=None,studentEmail=None):
    courseList = {}

    if instructorEmail != None:
        courseObject = Faculty.objects.get(email=instructorEmail).course_section.all()
        for course in courseObject:
            courseList[course.course_section_id] = course.course.course_title + " " + course.section_number

    elif studentEmail != None:
        classObject = Class.objects.all().filter(student=studentEmail).distinct()
        for individuaClass in classObject:
            course_section = individuaClass.course_section
            courseList[course_section.course_section_id] = course_section.course.course_title + " " + course_section.section_number

    requests.session['courseList'] = courseList


# Returns webscrapper info from csv():
def getTrailheadInformation(link):
    file_path = os.path.join(os.getcwd(),'clt_files','trailhead-points.csv')
    results = {}

    if len(link) == 0:
        return {'badge_count' : 0, 'points_count' : 0, 'trail_count' : 0, 'badges_obtained' : []}

    with open(file_path,mode='r+',encoding="utf-8") as csvInput:
        csv_reader = csv.reader(csvInput, delimiter=',')
        counter = 0

        for row in csv_reader:
            content = {}

            if counter == 0:
                counter += 1
            else:
                content['name'] = row[1]
                content['badge_count'] = row[2]
                content['points_count'] = row[3]
                content['trail_count'] = row[4]

                badges_obtained = row[5].split('|')
                new_badges_obtained = []
                for badge_obtained in badges_obtained:
                    new_badges_obtained.append(badge_obtained.replace(" ","_").lower())

                content['badges_obtained'] = new_badges_obtained
                results[row[0]] = content

    return results[link]

# The webscreapper to scrap static info from website
def webScrapper():
    from bs4 import BeautifulSoup
    input_file = 'clt_files/trailhead-url.txt'
    output_file = 'clt_files/trailhead-points.csv'
    st = time.time()
    # Get links from csv
    links = []
    with open(input_file, 'r') as file:
        for line in file:
            if len(line.strip()) > 0:
                links.append(line.strip())

    # Removes headers
    print("read link from file : %.9f " % (time.time()-st) )
    info = {}
    for link in links[1:]:
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

    with (open(output_file, 'w')) as file:
        writer = csv.writer(file)
        writer.writerow(['link', 'name', 'badges', 'points', 'trails', 'badges_obtained'])
        for link,content in info.items():
            to_write = [link, content['name'], content['badge-count'], content['points-count'], content['trail-count'], '|'.join(content['titles'])]
            writer.writerow(to_write)
    print("done scrapping info from  file : %.9f " % (time.time()-st) ) 

