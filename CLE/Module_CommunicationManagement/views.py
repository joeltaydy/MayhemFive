import traceback
from django.shortcuts import render
from Module_TeamManagement.models import *
from telethon.tl.types import Channel, Chat
from Module_Account.src import processLogin
from django.contrib.auth import logout, login
from Module_CommunicationManagement.src import tele_util, utilities

#----------------------------------------------#
#----------------Telegram Stuff----------------#
#----------------------------------------------#


# TO-DO: Main page for telegram management page
#
def faculty_telegram_Base(requests,response=None):
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
            response['telegram_chats'].append({'name': telegram_chat.name})

            members = tele_util.getMembers(client,telegram_chat.name,telegram_chat.type)
            telegram_chat.members = '_'.join(members)
            telegram_chat.save()

        if len(telegram_chats) > 0:
            if telegram_chat_name == None:
                first_chat = telegram_chats[0]
                response['current_telegram_chat'] = utilities.getTelegramChatJSON(first_chat)
            else:
                telegram_chat = Telegram_Chats.objects.get(name=telegram_chat_name)
                response['current_telegram_chat'] = utilities.getTelegramChatJSON(telegram_chat)

        # Note to self:
        # The problem here is that if the student doesn't join the group/channel
        # using the link we supplied via the cloudtopus, it won't be added into
        # the DB. (i.e. if their firends invite them into the group/channel)

        # Mitigation:
        # Restructure the method to do the same thing you did with the AMIs

        # However:
        # We won't be able to link the username is to the respective student

        # Mititgation for that: ?
        # <yet to figure out>

    except Exception as e:
        traceback.print_exc()
        response['error_message'] = 'Error during retrieval of Telegram details: ' + str(e.args[0])
        return render(requests,"Module_TeamManagement/Instructor/TelegramManagement.html",response)

    return render(requests,"Module_TeamManagement/Instructor/TelegramManagement.html",response)


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
    additional_username = requests.POST.get('username')
    course_section = requests.POST.get('course_section')
    print('Group Name: ' + group_name)
    print('Course Section: ' + course_section)
    print('Additional Username: ' + additional_username)

    try:
        username = requests.user.email.split('@')[0]
        client = tele_util.getClient(username)

        results = tele_util.initialize_Group(
            username=additional_username,
            client=client,
            group_name=group_name,
        )

        # Create Telegram_Chats object
        try:
            telegram_chat = Telegram_Chats.objects.create(
                name=group_name,
                type='Group',
                link=results['group_link'],
                members=None,
            )
            telegram_chat.save()
        except:
            telegram_chat = Telegram_Chats.objects.get(name=group_name)

        # Assign to the students of the course_section
        class_QuerySet = Class.objects.filter(course_section=course_section)
        for student in class_QuerySet:
            student.telegram_chats.add(telegram_chat)
            student.save()

        tele_util.disconnectClient(client)

    except Exception as e:
        traceback.print_exc()
        response['courses'] = requests.session['courseList_updated']
        response['error_message'] = 'Error during Telegram group creation: ' + str(e.args[0])
        return render(requests,"Module_TeamManagement/Instructor/TelegramManagement.html",response)

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
        username = requests.user.email.split('@')[0]
        client = tele_util.getClient(username)

        results = tele_util.initialize_Channel(
            client=client,
            channel_name=channel_name,
        )

        # Create Telegram_Chats object
        try:
            telegram_chat = Telegram_Chats.objects.create(
                name=channel_name,
                type='Channel',
                link=results['channel_link'],
                members=None,
            )
            telegram_chat.save()
        except:
            telegram_chat = Telegram_Chats.objects.get(name=channel_name)

        # Assign to the students of the course_section
        class_QuerySet = Class.objects.filter(course_section=course_section)
        for student in class_QuerySet:
            student.telegram_chats.add(telegram_chat)
            student.save()

        tele_util.disconnectClient(client)

    except Exception as e:
        traceback.print_exc()
        response['courses'] = requests.session['courseList_updated']
        response['error_message'] = 'Error during Telegram channel creation: ' + str(e.args[0])
        return render(requests,"Module_TeamManagement/Instructor/TelegramManagement.html",response)

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
    telegram_chat_link = requests.POST.get('telegram_chat_link')
    telegram_chat_type = requests.POST.get('telegram_chat_type')
    print('Telegram Chat Link: ' + telegram_chat_link)
    print('Telegram Chat Type: ' + telegram_chat_type)
    print('Message: ' + message)

    try:
        telegram_chatObj = Telegram_Chats.objects.get(link=telegram_chat_link)
        username = requests.user.email.split('@')[0]
        client = tele_util.getClient(username)

        if telegram_chat_type == 'Group':
            tele_util.sendGroupMessage(client,telegram_chatObj.name,message)
        elif telegram_chat_type == 'Channel':
            tele_util.sendChannelMessage(client,telegram_chatObj.name,message)

        tele_util.disconnectClient(client)

    except Exception as e:
        traceback.print_exc()
        response['courses'] = requests.session['courseList_updated']
        response['error_message'] = 'Error during Telegram channel creation: ' + str(e.args[0])
        return render(requests,"Module_TeamManagement/Instructor/TelegramManagement.html",response)

    return faculty_telegram_Base(requests,response)
