import json
import time
import traceback
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import HttpResponse
from Module_TeamManagement.models import *
from telethon.tl.types import Channel, Chat
from Module_Account.src import processLogin
from django.contrib.auth import logout, login
from Module_CommunicationManagement import tasks
from Module_CommunicationManagement.src import tele_util, utilities

#----------------------------------------------#
#----------------Telegram Stuff----------------#
#----------------------------------------------#


# Main page for telegram management page
#
def faculty_telegram_Base(requests,response=None):
    tele_chat_type = {
        'Channel':Channel,
        'Group':Chat,
    }

    if response == None:
        response = {"faculty_telegram_Base" : "active"}

    # Redirect user to login page if not authorized and faculty
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',response)

    if requests.method == "GET":
        course_section = requests.GET.get('course_section')
        telegram_chat_name = requests.GET.get('chat_name')
    else:
        course_section = requests.POST.get('course_section')
        telegram_chat_name = requests.POST.get('chat_name')

    if course_section == None:
        return render(requests,'Module_Account/login.html',response)

    try:
        # Retrieve Administritive Stuff
        courseList_updated = requests.session['courseList_updated']
        course_section = Course_Section.objects.get(course_section_id=course_section)
        response['course_sectionList'] = courseList_updated[course_section.course.course_title]

        if course_section.section_number == 'G0':
            to_string = course_section.course.course_title
        else:
            to_string= course_section.course.course_title + " " + course_section.section_number

        response['current_course_section_details'] = {
            'id':course_section.course_section_id,
            'course_title':course_section.course.course_title,
            'section_number':course_section.section_number,
            'to_string':course_section.to_string,
        }

        # Retrieve Telegram Stuff
        telegram_chats = Class.objects.filter(course_section=course_section)[0].telegram_chats.all()
        client = tele_util.getClient(requests.user.email.split('@')[0])

        response['telegram_chats'] = []
        for telegram_chat in telegram_chats:
            if tele_util.dialogExists(client,telegram_chat.name,tele_chat_type[telegram_chat.type]) or telegram_chat.link == None:
                response['telegram_chats'].append({'name': telegram_chat.name})
            else:
                telegram_chat.delete()

        if len(response['telegram_chats']) > 0:
            if telegram_chat_name == None:
                first_chat_name = telegram_chats[0].name
                response['current_telegram_chat'] = utilities.getTelegramChatJSON(chat_name=first_chat_name)
            else:
                telegram_chat = Telegram_Chats.objects.get(name=telegram_chat_name)
                response['current_telegram_chat'] = utilities.getTelegramChatJSON(chat_obj=telegram_chat)

        tele_util.disconnectClient(client)

    except Exception as e:
        traceback.print_exc()
        response['error_message'] = 'Error during retrieval of Telegram details: ' + str(e.args[0])
        return render(requests,"Module_TeamManagement/Instructor/TelegramManagement.html",response)

    return render(requests,"Module_TeamManagement/Instructor/TelegramManagement.html",response)


# Get all members in chat
#
def faculty_telegram_UpdateChatMembers(requests):
    response = {"faculty_telegram_UpdateChatMembers" : "active"}
    tele_chat_type = {
        'Channel':Channel,
        'Group':Chat,
    }

    # Redirect user to login page if not authorized and faculty
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',response)

    course_section = requests.POST.get('course_section')
    # telegram_chat_link = requests.POST.get('chat_link')
    telegram_chat_name = requests.POST.get('chat_name').replace('_',' ')
    # print('Telegram Chat Link: ' + telegram_chat_link)
    print('Telegram Chat Name: ' + telegram_chat_name)
    print('Course Section: ' + course_section)

    try:
        telegram_chat = Telegram_Chats.objects.get(name=telegram_chat_name)
        # telegram_chat = Telegram_Chats.objects.get(link=telegram_chat_link)

        client = tele_util.getClient(requests.user.email.split('@')[0])

        members, count = tele_util.getMembers(client,telegram_chat.name,tele_chat_type[telegram_chat.type])
        telegram_chat.members = '_'.join(members)
        telegram_chat.save()

        tele_util.disconnectClient(client)

    except Exception as e:
        traceback.print_exc()
        response['courses'] = requests.session['courseList_updated']
        response['error_message'] = 'Error during Telegram group creation: ' + str(e.args[0])
        return render(requests,"Module_TeamManagement/Instructor/TelegramManagement.html",response)

    requests.POST = requests.POST.copy()
    requests.POST['chat_name'] = telegram_chat_name
    response['message'] = 'Members successfully updated'
    return faculty_telegram_Base(requests,response)


# Group creation form
#
def faculty_telegram_CreateGroup(requests):
    response = {"faculty_telegram_CreateGroup" : "active"}

    # Redirect user to login page if not authorized and faculty
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',response)

    group_name = requests.POST.get('group_name')
    additional_username = '@rizzzy'
    course_section = requests.POST.get('course_section')
    print('Group Name: ' + group_name)
    print('Course Section: ' + course_section)
    print('Additional Username: ' + additional_username)

    try:
        # Create Telegram_Chats object
        try:
            telegram_chat = Telegram_Chats.objects.create(
                name=group_name,
                type='Group',
            )
            telegram_chat.save()
        except:
            telegram_chat = Telegram_Chats.objects.get(name=group_name)

        username = requests.user.email.split('@')[0]
        tasks.createGroup(
            username=username,
            group_name=group_name,
            additional_username=additional_username,
            schedule=5,
        )

        # Assign to the students of the course_section
        class_QuerySet = Class.objects.filter(course_section=course_section)
        for student in class_QuerySet:
            student.telegram_chats.add(telegram_chat)
            student.save()

    except Exception as e:
        traceback.print_exc()
        response['courses'] = requests.session['courseList_updated']
        response['error_message'] = 'Error during Telegram group creation: ' + str(e.args[0])
        return render(requests,"Module_TeamManagement/Instructor/TelegramManagement.html",response)

    response['message'] = 'Telegram Group successfully created'
    return faculty_telegram_Base(requests,response)


# Channel creation form
#
def faculty_telegram_CreateChannel(requests):
    response = {"faculty_telegram_CreateChannel" : "active"}

    # Redirect user to login page if not authorized and faculty
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',response)

    channel_name = requests.POST.get('channel_name')
    course_section = requests.POST.get('course_section')
    print('Channel Name: ' + channel_name)
    print('Course Section: ' + course_section)

    try:
        # Create Telegram_Chats object
        try:
            telegram_chat = Telegram_Chats.objects.create(
                name=channel_name,
                type='Channel',
            )
            telegram_chat.save()
        except:
            telegram_chat = Telegram_Chats.objects.get(name=channel_name)

        username = requests.user.email.split('@')[0]
        tasks.createChannel(
            username=username,
            channel_name=channel_name,
            schedule=5,
        )

        # Assign to the students of the course_section
        class_QuerySet = Class.objects.filter(course_section=course_section)
        for student in class_QuerySet:
            student.telegram_chats.add(telegram_chat)
            student.save()

    except Exception as e:
        traceback.print_exc()
        response['courses'] = requests.session['courseList_updated']
        response['error_message'] = 'Error during Telegram channel creation: ' + str(e.args[0])
        return render(requests,"Module_TeamManagement/Instructor/TelegramManagement.html",response)

    response['message'] = 'Telegram Channel successfully created'
    return faculty_telegram_Base(requests,response)


# Send message to designated section group/channel
#
def faculty_telegram_SendMessage(requests):
    response = {"faculty_telegram_SendMessage" : "active"}

    # Redirect user to login page if not authorized and faculty
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',response)

    message = requests.POST.get('message')
    # telegram_chat_link = requests.POST.get('telegram_chat_link')
    telegram_chat_type = requests.POST.get('telegram_chat_type')
    telegram_chat_name = requests.POST.get('telegram_chat_name').replace('_',' ')
    # print('Telegram Chat Link: ' + telegram_chat_link)
    print('Telegram Chat Type: ' + telegram_chat_type)
    print('Telegram Chat Name: ' + telegram_chat_name)
    print('Message: ' + message)

    try:
        if message == None:
            raise Exception('Please specify a message for broadcasting.')

        if requests.POST.get('datetime') == 'now' or requests.POST.get('setDate') == None:
            scheduled_datetime = datetime.now()
        else:
            scheduled_datetime = (datetime.strptime(requests.POST.get('setDate'),'%Y-%m-%dT%H:%M'))

        # if telegram_chat_link != None:
        #     telegram_chatObj = Telegram_Chats.objects.get(link=telegram_chat_link)

        period = scheduled_datetime - datetime.now()

        tasks.sendMessage(
            username=requests.user.email.split('@')[0],
            chat_type=telegram_chat_type,
            chat_name=telegram_chat_name,
            message=message,
            schedule=period,
        )

    except Exception as e:
        traceback.print_exc()
        response['courses'] = requests.session['courseList_updated']
        response['error_message'] = 'Error during Telegram channel creation: ' + str(e.args[0])
        return render(requests,"Module_TeamManagement/Instructor/TelegramManagement.html",response)

    requests.POST = requests.POST.copy()
    requests.POST['telegram_chat_name'] = telegram_chat_name
    response['message'] = 'Message successfully sent'
    return faculty_telegram_Base(requests,response)


# Supplmentary function for ajax call - to update the chat link for front end redirection
#
def faculty_telegram_GetChatLink(requests):
    response = { 'faculty_telegram_GetChatLink' : 'active'}

    # Redirect user to login page if not authorized and faculty
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',response)

    telegram_chat_name = requests.GET.get('telegram_chat_name')

    try:
        telegram_chatObj = Telegram_Chats.objects.get(name=telegram_chat_name)

        if telegram_chatObj.link == None:
            response['error_message'] = 'There no telegram chat link found in the database for that chat. Please check with administrator.'

        response['telegram_chat_link'] = telegram_chatObj.link
        response['telegram_chat_name'] = telegram_chat_name
    except:
        traceback.print_exc()

    return HttpResponse(json.dumps(response), content_type='application/json')


# Delete telegram group on demand
#
def faculty_telegram_DeleteChat(requests):
    response = { 'faculty_telegram_DeleteChat' : 'active'}

    # Redirect user to login page if not authorized and faculty
    try:
        processLogin.InstructorVerification(requests)
    except:
        logout(requests)
        return render(requests,'Module_Account/login.html',response)

    # telegram_chat_name = requests.POST.get('telegram_chat_name').replace('_',' ')
    # telegram_chat_type = requests.POST.get('telegram_chat_type')
    telegram_chat_name = 'Test'
    telegram_chat_type = 'Channel'
    print('Telegram Chat Type: ' + telegram_chat_type)
    print('Telegram Chat Name: ' + telegram_chat_name)

    try:
        facultyObj = Faculty.objects.get(email=requests.user.email)

        tasks.deleteChat(
            username=requests.user.email.split('@')[0],
            telegram_username=facultyObj.telegram_username,
            chat_name=telegram_chat_name,
            chat_type=telegram_chat_type,
            schedule=0,
        )

        telegram_chatObj = Telegram_Chats.objects.get(name=telegram_chat_name)
        telegram_chatObj.delete()
    except Exception as e:
        traceback.print_exc()
        response['courses'] = requests.session['courseList_updated']
        response['error_message'] = 'Error during Telegram channel creation: ' + str(e.args[0])
        return render(requests,"Module_TeamManagement/Instructor/TelegramManagement.html",response)

    response['message'] = 'Telegram chat successfully deleted'
    return faculty_telegram_Base(requests,response)
