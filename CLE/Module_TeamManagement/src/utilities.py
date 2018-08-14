import traceback
import requests
import json
import csv
import sys

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
    return


# Returns webscrapper info from csv():
def readScrapperCSV():
    file_name = 'trailhead-points.csv'
    results = {}

    with open(file_name) as csvInput:
        csv_reader = csv.reader(csvInput, delimiter=',')
        counter = 0

        for row in csv_reader:
            content = {}

            if counter == 0:
                counter += 1
            else:
                content['name'] = row[1]
                content['badge-count'] = row[2]
                content['points-count'] = row[3]
                content['trail-count'] = row[4]
                results[row[0]] = content

    return results


# The webscreapper to scrap static info from website
def webScrapper():
    input_file = 'trailhead-url.txt'
    output_file = 'trailhead-points.csv'

    # Get links from csv
    links = []
    with open(input_file, 'r') as file:
        for line in file:
            if len(line.strip()) > 0:
                links.append(line.strip())

    # Removes headers
    links = links[1:]
    links = links[1:]

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
        stats = soup.find_all(attrs={'class', 'user-information__achievements-data'})

        content['titles'] = titles
        content['name'] = json.loads(str(name['data-react-props']))['full_name']
        content['badge-count'] = stats[0].text.strip()
        content['points-count'] = stats[1].text.strip()
        content['trail-count'] = stats[2].text.strip()

        info[link] = content

    with (open(output_file, 'w')) as file:
        writer = csv.writer(file)
        writer.writerow(['link', 'name', 'badges', 'points', 'trails', 'badges_obtained'])
        for link,content in info.items():
            to_write = [link, content['name'], content['badge-count'], content['points-count'], content['trail-count'], '|'.join(content['titles'])]
            writer.writerow(to_write)


# FOR TESTING
if __name__ == "__main__":
    from bs4 import BeautifulSoup
    results = readScrapperCSV()
    print(results)
else:
    from Module_TeamManagement.models import *
