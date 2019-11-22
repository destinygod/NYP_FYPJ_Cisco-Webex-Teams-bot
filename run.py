from __future__ import print_function
import os
import requests
import pymysql
import datetime
from datetime import *
from webexteamsbot import TeamsBot
from webexteamsbot.models import Response

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/classroom.announcements' , 'https://www.googleapis.com/auth/classroom.courses' , 'https://www.googleapis.com/auth/classroom.coursework.me' , 'https://www.googleapis.com/auth/classroom.coursework.students' ]#coursework.students
# Retrieve required details from environment variables
bot_email = "limpehbot@webex.bot"
teams_token = "REDACTED" # use your own
bot_url = "https://df524144.ngrok.io" #enter your own NGROK address
bot_app_name = "limpehbotapp"

#database connection
def callldb(id):
    connection = pymysql.connect(host="127.0.0.1", user="root", password="", database="pythonbotdev")
    cursor = connection.cursor()
    #mysql statements here
    query = "SELECT * FROM userdata where id='%s';" % id
    cursor.execute(query)
    rows = cursor.fetchall()
    stringy =""
    for row in rows:
        stringy += str(row)
    connection.close()
    return stringy

# Create a Bot Object
bot = TeamsBot(
    bot_app_name,
    teams_bot_token=teams_token,
    teams_bot_url=bot_url,
    teams_bot_email=bot_email,
    debug=True,
)
#list of ID's, hardcode
moduleDictionary = [

    '44654655440',# software
    '7428202732', # web apps
    '44347432831' #developer
]
#connect id to name
moduleNameToId = {

    '7428202732':'Web Applications', # web apps
    '44654655440':'Software Development',# software
    '44347432831':'Developer class' #developer
}



global moduleList  # {"123456789":"Software development"}
global numberModule # {"1":"123456789"}
global numberModuleName # {"1":"Software development"} Only when user asks what modules they are enrolled in

# list down to user what modules they are enrolled in
def enrolled_modules(incoming_msg):
    return numberModuleName

# do not use for presentation
def getModuleListDict(incoming_msg): #dev function
    get_moduleListAuto()
    return str(moduleList) + str(numberModule) + str(numberModuleName)

#important. to populate the module dictionary reference
# do not use for presentation
def get_moduleListAuto():
    sender = "marc"
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('classroom', 'v1', credentials=creds)
    results = service.courses().list(pageSize=10).execute()
    courses = results.get('courses', [])

    if not courses:
        listofcourses = "No courses found"
    else:
        listofcourses = 'Courses: \n'
        thislist = []
        moduleList = {}  # actual module names with courseID
        numberModule = {}  # number with courseID
        numberModuleName = {}  # {1:software development} for reference only.

        thislist = []
        loop = 1
        # moduleList {  1:{id:module} , 2:{id:module}, 3:{id:module}  }
        for course in courses:
            # make my own list
            moduleList[course['id']] = course['name']  # { "123456789":"Software development"}
            numberModule[loop] = course['id']  # { "1":"123456789"} number it for users to make selection
            numberModuleName[loop] = course['name']  # {"1":"software dev"} reference only.s
            # moduleList[loop] = {course['id']: course['name']} #moduleList[1]= {"123456789":"software development"}
            thislist.append(str(loop) + " : " + course['name'])
            loop += 1

def get_moduleList(incoming_msg):
    sender = bot.teams.people.get(incoming_msg.personId)
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('classroom', 'v1', credentials=creds)
    results = service.courses().list(pageSize=10).execute()
    courses = results.get('courses', [])

    if not courses:
        listofcourses = "No courses found"
    else:
        listofcourses ='Courses: \n'
        thislist = []
        moduleList = {} # actual module names with courseID
        numberModule = {} # number with courseID
        numberModuleName = {} # {1:software development} for reference only.

        thislist = []
        loop =1
        # moduleList {  1:{id:module} , 2:{id:module}, 3:{id:module}  }
        for course in courses:
            # make my own list
            moduleList[course['id']] = course['name'] # { "123456789":"Software development"}
            numberModule[loop] = course['id'] # { "1":"123456789"} number it for users to make selection
            numberModuleName[loop] = course['name'] # {"1":"software dev"} reference only.s
            #moduleList[loop] = {course['id']: course['name']} #moduleList[1]= {"123456789":"software development"}
            thislist.append(str(loop) + " : " + course['name'])
            loop += 1

        values = "Hey there {}, these are the courses you are enrolled in \r\n\n".format(sender.firstName) + '\n\n'.join(str(v) for v in thislist)
    # if -dev parameter is given
    if str(incoming_msg.text) == "/get_modlist -dev":
        return str(values) + "\r\n\n" + str(numberModuleName) + "\r\n\n" + str(moduleList)
    else:
        return str(values)

# get courses enrolled in, does not populate dictionaries
def callgoogle(incoming_msg):
    sender = bot.teams.people.get(incoming_msg.personId)
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('classroom', 'v1', credentials=creds)

    results = service.courses().list(pageSize=10).execute()
    courses = results.get('courses', [])

    if not courses:
        listofcourses = "No courses found"
    else:
        listofcourses ='Courses: \n'
        thislist = []
        loop =1
        for course in courses:
            # make my own list
            thislist.append(str(loop) + " : " + course['name'])
            loop += 1
        #values = listofcourses + '-'.join(map(str, courses)) WORKING
        # now make my own list into concat strings and return
        values = "Hey there {}, these are the courses you are enrolled in \r\n\n".format(sender.firstName) + '\n\n'.join(str(v) for v in thislist) + "\n\nThat's all!"

    return values

# get announcements
def announcements_test(incoming_msg):
    """Shows basic usage of the Classroom API.
    Prints the names of the first 10 courses the user has access to.
    """
    sender = bot.teams.people.get(incoming_msg.personId)
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('classroom', 'v1', credentials=creds)

    # Call the Classroom API
    #results = service.courses().list(pageSize=10).execute()
    #courses = results.get('courses', [])
    values = "Hey there {}, Here are the announements \r\n\n".format(sender.firstName)
    for item in moduleDictionary:
        moduleName = moduleNameToId[item]
        # call the classroom api for courses
        results = service.courses().announcements().list(courseId=item).execute()
        announcements = results.get('announcements', [])
        if not announcements :
            listofannouncements = "No announcements found"
        else:
            listofannouncements ='Courses: \n'
            thislist = []
            loop =1
            for course in announcements:
                # make my own list
                thislist.append("[" + moduleName +"]" +"\r\n\n"+ " : " + course['text']+"\r\n\n")
                loop += 1
            #values = listofcourses + '-'.join(map(str, courses)) WORKING
            # now make my own list into concat strings and return
            values += '\n\n'.join(str(v) for v in thislist)

    return values + "That's all!"

# get coursework for 1 module
def work2do_module(incoming_msg, modnumber):
    print("todo function thingy lol")

def updateStudents(incoming_msg):
    sender = bot.teams.people.get(incoming_msg.personId)
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('classroom', 'v1', credentials=creds)

    # came from work2do 2. finding out how to do week,month,all. but first to call the courses.
    # i wanted to call this multiple times with hardcoded courseId.
    # or....just do a loop
    values = "hey there {}, Here are the coursework \r\n\n".format(sender.firstName)
    tester = ""
    loop = 1
    for item in moduleDictionary:
        tester += " test successful "
        results = service.courses().courseWork().list(courseId=item, courseWorkStates='PUBLISHED').execute()
        courseWork = results.get('courseWork', [])
        courseName = moduleNameToId[item]
        if not courseWork:
            return "no coursework found"
        else:
            thislist = []

            for course in courseWork:
                # make my own list
                # coursetitle, day/month/year hour:minute

                if item == "7428202732" and str(course["description"]) != "Build a web application":
                    thislist.append(
                          courseName + "\r\n\n" + str(loop) + " : " + "[ " + course['title'] + "]" + " Due at: " + str(
                            course["dueDate"]["day"]) + "/" + str(course["dueDate"]["month"]) + "/" + str(
                            course["dueDate"]["year"]) + " at time: " + str(course["dueTime"]["hours"]) + ":" + str(
                            course["dueTime"]["minutes"]) + "\r\n\n")
                    loop += 1
                    thislist.append("the following have been updated")
                elif item == "44654655440" and str(course["description"]) != "practical test 1 for software development":
                    thislist.append(
                         courseName + "\r\n\n" + str(loop) + " : " + "[ " + course[
                            'title'] + "]" + " Due at: " + str(
                            course["dueDate"]["day"]) + "/" + str(course["dueDate"]["month"]) + "/" + str(
                            course["dueDate"]["year"]) + " at time: " + str(course["dueTime"]["hours"]) + ":" + str(
                            course["dueTime"]["minutes"]) +"\r\n\n")
                    loop += 1
                    thislist.append("the following have been updated")
                elif item == "44347432831" and str(course["description"]) != "Instructions for final exam 2020":
                    thislist.append(
                        courseName + "\r\n\n" + str(loop) + " : " + "[ " + course[
                            'title'] + "]" + " Due at: " + str(
                            course["dueDate"]["day"]) + "/" + str(course["dueDate"]["month"]) + "/" + str(
                            course["dueDate"]["year"]) + " at time: " + str(course["dueTime"]["hours"]) + ":" + str(
                            course["dueTime"]["minutes"]) + "\r\n\n")
                    loop += 1
                    thislist.append("the following have been updated")
            # values = listofcourses + '-'.join(map(str, courses)) WORKING
            # now make my own list into concat strings and return
            values += '\n\n'.join(str(v) for v in thislist)
    # for loop end
    values += "\n\nThat's all! "
    return values

#work2do2, takes in module name/number as arguement
def work2do(incoming_msg): #selection

    sender = bot.teams.people.get(incoming_msg.personId)
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('classroom', 'v1', credentials=creds)

    results = service.courses().courseWork().list(courseId='7428202732', courseWorkStates='PUBLISHED').execute()
    courseWork = results.get('courseWork', [])
    if not courseWork:
        return "no coursework found"
    else:
        listofannouncements ='Courses: \n'
        thislist = []
        loop =1
        for course in courseWork:
            # make my own list
            # coursetitle, day/month/year hour:minute
            thislist.append(str(loop) + " : " + "[ "+course['title']+"]" + " Due at: " +str(course["dueDate"]["day"])+ "/" + str(course["dueDate"]["month"]) +"/"+ str(course["dueDate"]["year"]) + " at time: " + str(course["dueTime"]["hours"])+":"+ str(course["dueTime"]["minutes"]) +  str(course["dueTime"]["minutes"]))
            loop += 1
        #values = listofcourses + '-'.join(map(str, courses)) WORKING
        # now make my own list into concat strings and return
        values = "Hey there {}, Here are the coursework \r\n\n".format(sender.firstName) + '\n\n'.join(str(v) for v in thislist) + "\n\nThat's all!"

    return values

# get all coursework organized by date
def work2do2(incoming_msg):
    sender = bot.teams.people.get(incoming_msg.personId)
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('classroom', 'v1', credentials=creds)

    sender = bot.teams.people.get(incoming_msg.personId)
    # prompt user for their option
    if str(incoming_msg.text) == "/work2do week":
        values = "hey there {}, Here are the coursework \r\n\n".format(sender.firstName)
        loop = 1
        today = date.today()
        week = today + timedelta(days=7)
        for item in moduleDictionary:
            results = service.courses().courseWork().list(courseId=item, courseWorkStates='PUBLISHED').execute()
            courseWork = results.get('courseWork', [])
            courseName = moduleNameToId[item]
            if not courseWork:
                return "no coursework found"
            else:
                thislist = []

                for course in courseWork:
                    # make my own list
                    # coursetitle, day/month/year hour:minute
                    assignmentDueDate = date(course["dueDate"]["year"], course["dueDate"]["month"], course["dueDate"]["day"])
                    if assignmentDueDate < week:
                        thislist.append(
                            courseName + "\r\n\n" + str(loop) + " : " + "[ " + course['title'] + "]" + " Due at: " + str(
                                course["dueDate"]["day"]) + "/" + str(course["dueDate"]["month"]) + "/" + str(
                                course["dueDate"]["year"]) + " at time: " + str(course["dueTime"]["hours"]) + ":" + str(
                                course["dueTime"]["minutes"]) + str(course["description"])+"\r\n\n")# see how get desc, then conn to sql
                        loop += 1
                # values = listofcourses + '-'.join(map(str, courses)) WORKING
                # now make my own list into concat strings and return
                values += '\n\n'.join(str(v) for v in thislist)
        # for loop end
        values += "\n\nThat's all! "
        return values  # try the order by date
    elif str(incoming_msg.text) == "/work2do month":
        values = "hey there {}, Here are the coursework \r\n\n".format(sender.firstName)
        loop = 1
        today = date.today()
        week = today + timedelta(days=30)
        for item in moduleDictionary:
            results = service.courses().courseWork().list(courseId=item, courseWorkStates='PUBLISHED').execute()
            courseWork = results.get('courseWork', [])
            courseName = moduleNameToId[item]
            if not courseWork:
                return "no coursework found"
            else:
                thislist = []

                for course in courseWork:
                    # make my own list
                    # coursetitle, day/month/year hour:minute
                    assignmentDueDate = date(course["dueDate"]["year"], course["dueDate"]["month"],
                                             course["dueDate"]["day"])
                    if assignmentDueDate < week:
                        thislist.append(
                            courseName + "\r\n\n" + str(loop) + " : " + "[ " + course[
                                'title'] + "]" + " Due at: " + str(
                                course["dueDate"]["day"]) + "/" + str(course["dueDate"]["month"]) + "/" + str(
                                course["dueDate"]["year"]) + " at time: " + str(course["dueTime"]["hours"]) + ":" + str(
                                course["dueTime"]["minutes"]) + "\r\n\n")
                        loop += 1
                # values = listofcourses + '-'.join(map(str, courses)) WORKING
                # now make my own list into concat strings and return
                values += '\n\n'.join(str(v) for v in thislist)
        # for loop end
        values += "\n\nThat's all! "
        return values  # try the order by date
    elif str(incoming_msg.text) == "/work2do all":
        return work2doALL(incoming_msg)
    else:
        return "Hi {}, i can get your work for you. Simply tell me which order to get them by\r\n\n".format(sender.firstName) + "\n **week** - gets weekly work\n" + "\n **month** - get monthly work\n" + "\n **all** - gets all available outstanding work\n" + "\ne.g /work2do month"

# test if i can call the service multiple times lol
def work2doALL(incoming_msg):

    sender = bot.teams.people.get(incoming_msg.personId)
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('classroom', 'v1', credentials=creds)

    # came from work2do 2. finding out how to do week,month,all. but first to call the courses.
    # i wanted to call this multiple times with hardcoded courseId.
    # or....just do a loop
    values = "hey there {}, Here are the coursework \r\n\n".format(sender.firstName)
    tester = ""
    loop = 1
    for item in moduleDictionary:
        tester+= " test successful "
        results = service.courses().courseWork().list(courseId=item, courseWorkStates='PUBLISHED').execute()
        courseWork = results.get('courseWork', [])
        courseName = moduleNameToId[item]
        if not courseWork:
            return "no coursework found"
        else:
            thislist = []

            for course in courseWork:
                # make my own list
                # coursetitle, day/month/year hour:minute
                thislist.append(courseName + "\r\n\n" + str(loop) + " : " + "[ " + course['title'] + "]" + " Due at: " + str(
                    course["dueDate"]["day"]) + "/" + str(course["dueDate"]["month"]) + "/" + str(
                    course["dueDate"]["year"]) + " at time: " + str(course["dueTime"]["hours"]) + ":" + str(
                    course["dueTime"]["minutes"]) +"\r\n\n")
                loop += 1
            # values = listofcourses + '-'.join(map(str, courses)) WORKING
            # now make my own list into concat strings and return
            values += '\n\n'.join(str(v) for v in thislist)
    # for loop end
    values += "\n\nThat's all! "
    return values

def work2doWEEK(incoming_msg):

    sender = bot.teams.people.get(incoming_msg.personId)
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('classroom', 'v1', credentials=creds)

    # came from work2do 2. finding out how to do week,month,all. but first to call the courses.
    # i wanted to call this multiple times with hardcoded courseId.
    # or....just do a loop
    values = "hey there {}, Here are the coursework \r\n\n".format(sender.firstName)
    tester = ""
    loop = 1
    for item in moduleDictionary:
        tester+= " test successful "
        results = service.courses().courseWork().list(courseId=item, courseWorkStates='PUBLISHED').execute()
        courseWork = results.get('courseWork', [])
        courseName = moduleNameToId[item]
        if not courseWork:
            return "no coursework found"
        else:
            thislist = []

            for course in courseWork:
                # make my own list
                # coursetitle, day/month/year hour:minute
                thislist.append(courseName + "\r\n\n" + str(loop) + " : " + "[ " + course['title'] + "]" + " Due at: " + str(
                    course["dueDate"]["day"]) + "/" + str(course["dueDate"]["month"]) + "/" + str(
                    course["dueDate"]["year"]) + " at time: " + str(course["dueTime"]["hours"]) + ":" + str(
                    course["dueTime"]["minutes"]) +"\r\n\n")
                loop += 1
            # values = listofcourses + '-'.join(map(str, courses)) WORKING
            # now make my own list into concat strings and return
            values += '\n\n'.join(str(v) for v in thislist)
    # for loop end
    values += "\n\nThat's all! "
    return values

# Create a custom bot greeting function returned when no command is given.
# The default behavior of the bot is to return the '/help' command response
def greeting(incoming_msg):
    # Loopkup details about sender

    sender = bot.teams.people.get(incoming_msg.personId)
    if incoming_msg.text == "what outstanding assignments do i have":
        answer = Response()
        answer.markdown = "Hey {}, Here is what you have to do".format(sender.firstName) + work2do(incoming_msg)

        return answer
    else:
        # Create a Response object and craft a reply in Markdown.
        response = Response()

        response.markdown = "Hello {}, I'm a chat bot. ".format(sender.firstName)
        response.markdown += "See what I can do by asking for **/help**."
        return response


# A simple command that returns a basic string that will be sent as a reply
def do_something(incoming_msg):
    """
    Sample function to do some action.
    :param incoming_msg: The incoming message object from Teams
    :return: A text or markdown based reply
    """
    listofcourses = callgoogle(incoming_msg)
    return listofcourses


# An example using a Response object.  Response objects allow more complex
# replies including sending files, html, markdown, or text. Rsponse objects
# can also set a roomId to send response to a different room from where
# incoming message was recieved.
def picture_message(incoming_msg):
    """
    Sample function that uses a Response object for more options.
    :param incoming_msg: The incoming message object from Teams
    :return: A Response object based reply
    """
    # Create a object to create a reply.
    response = Response()

    # Set the text of the reply.
    response.text = "Here's a fun little meme."

    # Craft a URL for a file to attach to message
    u = "https://sayingimages.com/wp-content/uploads/"
    u = u + "aaaaaalll-righty-then-alrighty-meme.jpg"
    response.files = u
    return response


# An example command the illustrates using details from incoming message within
# the command processing.
def current_time(incoming_msg):
    """
    Sample function that returns the current time for a provided timezone
    :param incoming_msg: The incoming message object from Teams
    :return: A Response object based reply
    """
    # Extract the message content, without the command "/time"
    timezone = bot.extract_message("/time", incoming_msg.text).strip()

    # Craft REST API URL to retrieve current time
    #   Using API from http://worldclockapi.com
    u = "http://worldclockapi.com/api/json/{timezone}/now".format(
        timezone=timezone
    )
    r = requests.get(u).json()

    # If an invalid timezone is provided, the serviceResponse will include
    # error message
    if r["serviceResponse"]:
        return "Error: " + r["serviceResponse"]

    # Format of returned data is "YYYY-MM-DDTHH:MM<OFFSET>"
    #   Example "2018-11-11T22:09-05:00"
    returned_data = r["currentDateTime"].split("T")
    cur_date = returned_data[0]
    cur_time = returned_data[1][:5]
    timezone_name = r["timeZoneName"]

    # Craft a reply string.
    reply = "In {TZ} it is currently {TIME} on {DATE}.".format(
        TZ=timezone_name, TIME=cur_time, DATE=cur_date
    )
    return reply

#send a meme
def meme_func(incoming_msg):
    response = Response()
    for x in range(1):
        response.files = "https://media.giphy.com/media/jKWVkeDxquixAE1gDW/giphy.gif" #jojo dora
        return response

    Response.text = "Food for your chronic meme addiction"

def deletePickle(incoming_msg):
    import os
    if os.path.exists("C:\\Users\\Marcus Low\\Desktop\\FYP\\Python bot\\token.pickle"):
        os.remove("token.pickle")
        return "Token.pickle has been removed"
    else:
        return "token.pickle failed to remove"

# Create help message for current_time command
current_time_help = "Look up the current time for a given timezone. "
current_time_help += "_Example: **/time EST**_"

# Set the bot greeting.
bot.set_greeting(greeting)

# Add new commands to the box.


# uncommenting for presentation bot.add_command("/time", current_time_help, current_time)
bot.add_command("/updates", "[Working] Gets any updates made to existing work", updateStudents)
bot.add_command("/announcements", "[Working] Gets announcements from all courses", announcements_test)
bot.add_command("/work2do", "[Working] Gets outstanding work, organizable by time", work2do2)
bot.add_command("/worklist", "[Working] Gets your outstanding work to do from all courses [new func]", work2doALL)
bot.add_command("/get_modlist", "[Working] Get list of enrolled courses (args: -dev)",get_moduleList)

#bot.add_command("/db", "[Developer function] - Test connection to database with calldb()", callldb)
#bot.add_command("/dosomething", "[Developer function] - returns list of enrolled courses from callgoogle()", do_something)
#bot.add_command("/demo", "[Developer function] - send message with picture attached", picture_message)
#bot.add_command("/pickle", "[Developer function] - delete token.pickle", deletePickle)
#bot.add_command("/checkMods", "[Developer function] - check if dictionaries are populated", getModuleListDict)
#bot.add_command("/oldwork2do", "[Developer function] - check work to do, old function", work2do)
# Every bot includes a default "/echo" command.  You can remove it, or any
# other command with the remove_command(command) method.
bot.remove_command("/echo")

if __name__ == "__main__":
    # Run Bot
    bot.run(host="0.0.0.0", port=6969)
    #get_moduleList()
    #get_moduleListAuto();
