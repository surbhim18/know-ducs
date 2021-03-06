import random
import boto3
import time
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, speech_output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': speech_output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': speech_output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_dialog_elicit_speechlet(slot_name, intent, title, speech_output, reprompt_text):
    return{
        'outputSpeech': {
            'type': 'PlainText',
            'text': speech_output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': speech_output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        
        'shouldEndSession': False,
        
        'directives':  [{
            "type": "Dialog.ElicitSlot",
            "slotToElicit": slot_name,
            "updatedIntent": {
                "name": intent['name'],
                "confirmationStatus": "NONE",
                "slots": intent['slots'] 
            }}]
        }

def build_dialog_auto_speechlet():
    return{
        'shouldEndSession': False,
        'directives':  [{
        "type": "Dialog.Delegate",
        }]
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

# ---------------------------- Data for the skill ------------------------------

possibleCategory = {'general','obc','sc','st','pwd'}
possibleGender = {'female','male'}
possibleCourse = {'M.Sc. Computer Science','MCA','PhD'}

subCodeSem = {'MCS-301':3,'MCS-311':3,'MCS-312':3,'MCS-313':3 ,'MCS-316':3,'MCS-326':3 }
subCodeSem2 = {3: ['MCS-301','MCS-311','MCS-312','MCS-313','MCS-316','MCS-326'] }
subCodeSubName = {'MCS-301':'Minor Project','MCS-311':'Algorithms','MCS-312':'Data mining','MCS-313':'Network Science' ,'MCS-316':'Operating Systems','MCS-326':'Information security'}

# --------------------------- Global variables ---------------------------------


# --------------- Functions that control the skill's behavior ------------------

welcome_greetings = ["Hello! ","Howdy! ","Hi! "]

def get_welcome_response():
    
    session_attributes = {}
    card_title = "Welcome"
    wel = welcome_greetings[random.randint(0,len(welcome_greetings)-1)]
    
    speech_output = wel + "Welcome! Ask any admission or result related queries!."
    reprompt_text = "For help, say help!"
    
    should_end_session = False
    
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def clear_session_attributes():
    session_attributes = {}

def is_in_intent(intent,slot_name):
    if 'value' in intent['slots'][slot_name]:
        return True
        
    return False
    
def is_in_session_attributes(key):
    if key in session_attributes:
        return True
    
    return False

# ------------------------------------------------ result queries begin ------------------------------------------------- #

def res_query_1(intent, session, course, batch, subject, rollno):
    #subject tells semester
    
    #global subCodeSubName
    #global subCodeSem
    
    semester = subCodeSem[subject]
    table_name = "Result_Batch_"+batch
    table = dynamodb.Table(table_name)
    
    subList = []
    if(subject == 'MCS-301'):
        subList.append(subject)
    else:
        subList.append(subject+"_IA")
        subList.append(subject+"_W")
        
    response = table.query(
            KeyConditionExpression=Key('roll_no').eq(rollno) & Key('semester').eq(str(semester)) 
        )
    
    item = response['Items']
    print(item)
    name = item[0]['name']
    marks = 0
    flag = 0
    for s in subList:
        if(item[0][s]=='xxxx'):
            flag = -1
        #print(int(item[0][s]))
        else:
            marks += int(item[0][s])
    
    if(flag == -1):
        res = "Oops! " + name + " did not opt for this subject"
    else:
        res = name+ " scored "+ str(marks) + " in "+ subCodeSubName[subject[0:7]]
        
    card_title = "1"
    speech_output = res
    reprompt_text = ""
    should_end_session = False
    
    clear_session_attributes()
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def res_query_2(intent, session, course, batch, semester, rollno):
    
    #global subCodeSem2
    table_name = "Result_Batch_"+batch
    table = dynamodb.Table(table_name)
    
    response = table.query(
            KeyConditionExpression=Key('roll_no').eq(rollno) & Key('semester').eq(semester) 
        )
    item = response['Items']
    name = item[0]['name']
    
    allSubjects = subCodeSem2[int(semester)]
    
    subList = []
    for s in allSubjects:
        #if s == 'MCS-301':
        subList.append(s)
        """
        else:
            subList.append(s+"_IA")
            subList.append(s+"_W")
        """    
    print(type(item[0]))   
    res = "Student Name is " + name+","
    for s in subList:
        x= str(s+"_IA")
        print(x)
        if x in item[0]:
            if item[0][x] == "xxxx":
                temp = 0
            else:
                #internal = str(s+_"IA")
                theory= str(s+"_W")
                res += "Marks in " + subCodeSubName[s[0:7]] + " are " + str(int(item[0][x])+int(item[0][theory])) +", "
        else:
            if item[0][s] == "xxxx":
                temp = 0
            else:
                res += "Marks in " + subCodeSubName[s[0:7]] + " are " + item[0][s] +", "
    card_title = "2"
    speech_output = res
    reprompt_text = ""
    should_end_session = False
    
    clear_session_attributes()
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def res_query_3(intent, session, course, batch, semester, subject, rollno):
    #check if subject matches semester
    #define query here
    table_name = "Result_Batch_"+batch
    table = dynamodb.Table(table_name)
    
    subList = []
    if(subject == 'MCS-301'):
        subList.append(subject)
    else:
        subList.append(subject+"_IA")
        subList.append(subject+"_W")
        
    response = table.query(
            KeyConditionExpression=Key('roll_no').eq(rollno) & Key('semester').eq(semester) 
        )
    item = response['Items']
    name = item[0]['name']
    marks= []
    for s in subList:
        marks.append(item[0][s])
    
    if (subject =='MCS-301'):
        res = "Student name is "+ name+ " and marks in "+subCodeSubName[subject[0:7]] +" are "+ marks[0]
        
    else:
        res = "Student name is "+ name+ " and marks in "+ subCodeSubName[subject[0:7]] +" are "+ marks[0]+" in internals and "+marks[1] + " in theory"
    
    card_title = "3"
    speech_output = res
    reprompt_text = ""
    should_end_session = False
    
    clear_session_attributes()
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
    
def res_query_4(intent, session, course, batch, subject, stat):
    #subject tells semester
    #define query here
    
    #global subCodeSem
    semester = str(subCodeSem[subject])
    table_name = "Result_Batch_"+batch
    table = dynamodb.Table(table_name)
    response = table.query(KeyConditionExpression=Key('semester').eq(str(semester)))
    items = response['Items']
    
    if stat == "1":
        x= str(subject+"_IA")
        if(x not in items[0]):
            total = 0
            count = 0
            for item in items:
                if(item[subject] == 'xxxx'):
                    temp = 0
                else:
                    total += int(item[subject])
                    count += 1
            avg = total/count
            res = "the average marks in "+subCodeSubName[subject[0:7]]+ " for batch " +batch+" and semester "+semester+ " is " + str(round(avg,2))
        else:
            total = 0
            avg = 0
            count = 0
            y = str(subject+"_W")
            for item in items:
                if(item[x] == 'xxxx'):
                    temp = 0
                else:
                    total += int(item[x])
                    total += int(item[y])
                    count += 1
            avg = total/count
            res = "The average marks in "+subCodeSubName[subject[0:7]]+ " for batch " +batch+" and semester "+semester+ " is " + str(round(avg,2))+", "
    elif stat == "3":
        x= str(subject+"_IA")
        if(x not in items[0]):
            min = 1000
            for item in items:
                if(item[subject] == 'xxxx'):
                    temp = 0
                else:
                    if(int(item[subject])<min):
                        name = item['name']
                        min = int(item[subject])
            res = "the minimum marks in "+subCodeSubName[subject[0:7]]+ " is " + str(min)+" ,scored by "+name
        else:
            min = 1000
            y = str(subject+"_W")
            for item in items:
                if(item[x] == 'xxxx'):
                    temp = 0
                else:
                    total = int(item[x]) + int(item[y])
                    if(total<min):
                        name = item['name']
                        min = total
            res = "The minimum marks in "+subCodeSubName[subject[0:7]]+ " is " + str(min)+" ,scored by "+name
    elif stat == "2":
        x= str(subject+"_IA")
        if(x not in items[0]):
            max = -1
            for item in items:
                if(item[subject] == 'xxxx'):
                    temp = 0
                else:
                    if(int(item[subject])>max):
                        max = int(item[subject])
                        name = item['name']
            res = "The maximum marks in "+subCodeSubName[subject[0:7]]+ " is " + str(max)+" ,scored by "+name
        else:
            max = -1
            y = str(subject+"_W")
            for item in items:
                if(item[x] == 'xxxx'):
                    temp = 0
                else:
                    total = int(item[x]) + int(item[y])
                    #print(type(item[s]))
                    #print(type(int(item[s])))
                    if(total > max):
                        name = item['name']
                        max = total
            res = "The maximum marks in "+subCodeSubName[subject[0:7]]+ " is " + str(max)+" ,scored by "+name
    card_title = "4"
    speech_output = res
    reprompt_text = ""
    should_end_session = False
    
    clear_session_attributes()
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def res_query_5(intent, session, course, batch, semester, stat):
    #all subjects
    #define query here
    
    #global subCodeSem2
    allSubjects = subCodeSem2[int(semester)]
    
    subList = []
    for s in allSubjects:
        #if s == 'MCS-301':
        subList.append(s)
        """
        else:
            subList.append(s+"_IA")
            subList.append(s+"_W")
        """    
    table_name = "Result_Batch_"+batch
    table = dynamodb.Table(table_name)
    response = table.query( KeyConditionExpression=Key('semester').eq(semester) )
    items = response['Items']
    
    
    if stat == "1":
        res = "For batch " + batch + " and semester " + semester+". the average marks are as follows, " 
        for s in subList:
            x= str(s+"_IA")
            print(x)
            print(items)
            if(x not in items[0]):
                total = 0
                count = 0
                for item in items:
                    if(item[s] == 'xxxx'):
                        print('xxxx')
                        temp = 0
                    else:
                        total += int(item[s])
                        count += 1
                avg = total/count
                res += "in "+subCodeSubName[s[0:7]]+ " are " + str(round(avg,2))+', '
            else:
                total = 0
                avg = 0
                count = 0
                y = str(s+"_W")
                for item in items:
                    if(item[x] == 'xxxx'):
                        print('xxxx')
                    else:
                        total += int(item[x])
                        total += int(item[y])
                        count += 1
                avg = total/count
                res += "in "+ subCodeSubName[s[0:7]]+ " are " + str(round(avg,2))+" ,"
    elif stat == "3":
        res = "For batch " + batch + " and semester " + semester+". the minimum marks are as follows, " 
        for s in subList:
            x= str(s+"_IA")
            if(x not in items[0]):
                min = 1000
                for item in items:
                    if(item[s] == 'xxxx'):
                        temp = 0
                    else:
                        if(int(item[s])<min):
                            name = item['name']
                            min = int(item[s])
                res += "the minimum marks in "+subCodeSubName[s[0:7]]+ " is " + str(min)+" ,scored by "+name+" , "
            else:
                min = 1000
                y = str(s+"_W")
                for item in items:
                    if(item[x] == 'xxxx'):
                        temp = 0
                    else:
                        total = int(item[x]) + int(item[y])
                        if(total<min):
                            name = item['name']
                            min = total
                res += "The minimum marks in "+subCodeSubName[s[0:7]]+ " is " + str(min)+" ,scored by "+name+" , "
                
    elif stat == "2":
        res = "For batch " + batch + " and semester " + semester+". the max marks are as follows, " 
        for s in subList:
            x= str(s+"_IA")
            if(x not in items[0]):
                max = -1
                for item in items:
                    if(item[s] == 'xxxx'):
                        temp = 0
                    else:
                        if(int(item[s])>max):
                            max = int(item[s])
                            name = item['name']
                res += "The maximum marks in "+subCodeSubName[s[0:7]]+ " is " + str(max)+" ,scored by "+name+" , "
            else:
                max = -1
                y = str(s+"_W")
                for item in items:
                    if(item[x] == 'xxxx'):
                        temp = 0
                    else:
                        total = int(item[x]) + int(item[y])
                        #print(type(item[s]))
                        #print(type(int(item[s])))
                        if(total > max):
                            max = total
                            name = item['name']
                res += "The maximum marks in "+subCodeSubName[s[0:7]]+ " is " + str(max)+" ,scored by "+name+" , "
    
                
    card_title = "5"
    speech_output = res
    reprompt_text = ""
    should_end_session = False
    
    clear_session_attributes()
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def res_query_6(intent, session, course, batch, semester, subject, stat):
    #check if subject matches semester
    #define query here
    
    subList = []
    if(subject == 'MCS-301'):
        subList.append(subject)
    else:
        subList.append(subject+"_IA")
        subList.append(subject+"_W")
    table_name = "Result_Batch_"+batch
    table = dynamodb.Table(table_name)
    response = table.query( KeyConditionExpression=Key('semester').eq(semester) )
    items = response['Items']
    
    if stat == "1":
        if(subject =='MCS-301'):
            total = 0
            count = 0
            for item in items:
                if(item[subList[0]] == 'xxxx'):
                    temp = 0
                else:
                    total += int(item[subList[0]])
                    count += 1
            avg = total/count
            res = "the average marks in "+subCodeSubName[subject[0:7]]+ " for batch " +batch+" and semester "+semester+ " is " + str(round(avg,2))
        else:
            total = 0
            avg = 0
            count = 0
            for item in items:
                if(item[subList[0]] == 'xxxx'):
                    temp = 0
                else:
                    total += int(item[subList[0]])
                    total += int(item[subList[1]])
                    count += 1
            avg = total/count
            res = "The average marks in "+subCodeSubName[subject[0:7]]+ " for batch " +batch+" and semester "+semester+ " is " + str(round(avg,2))+" , "
    
    elif stat == '3':
        if(subject =='MCS-301'):
            min = 1000
            for item in items:
                if(item[subList[0]] == 'xxxx'):
                    temp = 0
                else:
                    if(int(item[subList[0]])<min):
                        min = int(item[subList[0]])
                        name = item['name']
            res = "the minimum marks in "+subCodeSubName[subject[0:7]]+ " for batch " +batch+" and semester "+semester+ " is " + str(min)+" ,scored by "+name
        else:
            min = 1000
            for item in items:
                if(item[subList[0]] == 'xxxx'):
                    temp = 0
                else:
                    total = int(item[subList[0]]) + int(item[subList[1]])
                    if(total < min):
                        min = total
                        name = item['name']
            res = "The minimum marks in "+subCodeSubName[subject[0:7]]+ " for batch " +batch+" and semester "+semester+ " is " + str(min)+" ,scored by "+name
    
    elif stat == '2':
        if(subject =='MCS-301'):
            max = -1
            for item in items:
                if(item[subList[0]] == 'xxxx'):
                    temp = 0
                else:
                    if(int(item[subList[0]])>max):
                        max = int(item[subList[0]])
                        name = item['name']
            res = "the maximum marks in "+subCodeSubName[subject[0:7]]+ " for batch " +batch+" and semester "+semester+ " is " + str(max)+" ,scored by "+name
        else:
            max = -1
            for item in items:
                if(item[subList[0]] == 'xxxx'):
                    temp = 0
                else:
                    total = int(item[subList[0]]) + int(item[subList[1]]) 
                    if(total > max):
                        max = total
                        name = item['name']
            res = "The maximum marks in "+subCodeSubName[subject[0:7]]+ " for batch " +batch+" and semester "+semester+ " is " + str(max)+" ,scored by "+name
    
    card_title = "6"
    speech_output = res
    reprompt_text = ""
    should_end_session = False
    
    clear_session_attributes()
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def result(intent, session):
    
    card_title = "Result"
    intent_name = intent['name']
    
    existsCourse = False
    existsBatch = False
    existsSemester = False
    existsSubject = False
    existsRollno = False
    existsStat = False
   
    if is_in_intent(intent,'course'):
        course = intent['slots']['course']['value']
        existsCourse = True
        session_attributes['course'] = course
  
    if is_in_intent(intent,'batch'):
        batch = intent['slots']['batch']['value']
        existsBatch = True
        session_attributes['batch'] = batch
   
    if is_in_intent(intent,'semester'):
        semester = intent['slots']['semester']['value']
        existsSemester = True
        session_attributes['semester'] = semester
    
    if is_in_intent(intent,'subject'):
        subject = intent['slots']['subject']["resolutions"]["resolutionsPerAuthority"][0]["values"][0]["value"]["id"]
        #subject = event["request"]["intent"]["slots"]["subject"]["resolutions"]["resolutionsPerAuthority"][0]["values"][0]["value"]["id"]
        existsSubject = True
        session_attributes['subject'] = subject
    
    if is_in_intent(intent,'rollno'):
        rollno = intent['slots']['rollno']['value']
        existsRollno = True
        session_attributes['rollno'] = rollno
        
    if is_in_intent(intent,'stat'):
        stat = intent['slots']['stat']["resolutions"]["resolutionsPerAuthority"][0]["values"][0]["value"]["id"]
        existsStat = True
        session_attributes['stat'] = stat
        print(session_attributes['stat'])
        print(type(session_attributes['stat']))
        
    reprompt_text = ""
    
    if not existsCourse:
        speech_output = "Don't try to fool me. Give me the course."
        return build_response(session_attributes, build_dialog_elicit_speechlet("course", intent, card_title, speech_output, reprompt_text))
    
    if not existsBatch:
        speech_output = "You seem clever, but I am more. Now, give me the batch."
        return build_response(session_attributes, build_dialog_elicit_speechlet("batch", intent, card_title, speech_output, reprompt_text))
    
    if existsStat:
        #query 4,5,6
        if existsSemester and existsSubject:
            #query 6
            return res_query_6(intent, session, course, batch, semester, subject, stat)
        elif existsSemester:
            #query 5
            return res_query_5(intent, session, course, batch, semester, stat)
        elif existsSubject:
            #query 4
            return res_query_4(intent, session, course, batch, subject, stat)
        else:
            #we have neither subject nor semester
            #elicit subject
            speech_output = "you seem to have forgot to provide the subject, what's the subject"
            return build_response(session_attributes, build_dialog_elicit_speechlet("subject", intent, card_title, speech_output, reprompt_text))
    elif existsRollno:
        #query 1,2,3
        if existsSemester and existsSubject:
            #query 3
            return res_query_3(intent, session, course, batch, semester, subject, rollno)
        elif existsSubject:
            #query 1
            return res_query_1(intent, session, course, batch, subject, rollno)
        elif existsSemester:
            #query 2
            return res_query_2(intent, session, course, batch, semester, rollno)
        else:
            #we have neither subject or semester
            #elicit subject
            speech_output = "you seem to have forgot to provide the subject, what's the subject"
            return build_response(session_attributes, build_dialog_elicit_speechlet("subject", intent, card_title, speech_output, reprompt_text))
    else:
        speech_output = "you seem to have provided wrong query format, you can always ask for help or try again"
        return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
       
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

# ------------------------------------------------- result queries end ------------------------------------------------- #

# ---------------------------------------------- admission queries begin ----------------------------------------------- #

def adm_query_1(intent, session, batch):
    #nothing but batch
    #how many students were admitted in the year {batch}
    
    card_title = "Admission Query"
    
    table_name = "Admission_"+batch
    
    course = 'M.Sc. Computer Science'
    table = dynamodb.Table(table_name)
    
    response = table.query(
        KeyConditionExpression=Key('programme').eq(course)
    )
    if len(response["Items"]) > 0:
        items = response['Items']
        totalMsc = int(items[0]['gen_female'])+int(items[0]['gen_male'])+int(items[0]['obc_female'])+int(items[0]['obc_male'])+int(items[0]['pwd_female'])+int(items[0]['pwd_male'])+int(items[0]['sc_female'])+int(items[0]['sc_male'])+int(items[0]['st_female'])+int(items[0]['st_male'])
    else:
        output = "No record found for this year"
        return output
        
    course = "MCA"
    response = table.query(
        KeyConditionExpression=Key('programme').eq(course)  
    )
    if len(response["Items"]) > 0:
        items = response['Items']
        totalMca = int(items[0]['gen_female'])+int(items[0]['gen_male'])+int(items[0]['obc_female'])+int(items[0]['obc_male'])+int(items[0]['pwd_female'])+int(items[0]['pwd_male'])+int(items[0]['sc_female'])+int(items[0]['sc_male'])+int(items[0]['st_female'])+int(items[0]['st_male'])
    else:
        output = "No record found for this year"
        return output
        
    course = "PhD"
    response = table.query(
        KeyConditionExpression=Key('programme').eq(course)  
    )
    if len(response["Items"]) > 0:
        items = response['Items']
        totalPhd = int(items[0]['gen_female'])+int(items[0]['gen_male'])+int(items[0]['obc_female'])+int(items[0]['obc_male'])+int(items[0]['pwd_female'])+int(items[0]['pwd_male'])+int(items[0]['sc_female'])+int(items[0]['sc_male'])+int(items[0]['st_female'])+int(items[0]['st_male'])
    else:
        output = "No record found for this year"
        return output
        
    totalStudents = totalMsc+totalMca+totalPhd
    output = "The number of students admitted in the year "+batch+" is "+str(totalStudents)
   
    clear_session_attributes()
    return output
    
def adm_query_2(intent, session, batch, course):
    #batch and course given
    #how many students were admitted to the course {course} in the year {batch}
    
    card_title = "Admission Query"

    if course == 'msc' or course == 'msc computer science' or course == 'MSc':
        course = "M.Sc. Computer Science"
    elif course == 'mca' or course == 'masters in computer applications' or course == 'masters in computer application':
        course = "MCA"
    elif course == 'phd' or course == 'doctrate' or course == 'doctrate in philosophy':
        course = "PhD"
        
    if course not in possibleCourse:
        output = "Sorry, I was not able to process the course."
        return output
        
    table_name = "Admission_"+batch
    
    table = dynamodb.Table(table_name)
    
    response = table.query(
        KeyConditionExpression=Key('programme').eq(course)  
    )
    if len(response["Items"]) > 0:
        items = response['Items']
        total = int(items[0]['gen_female'])+int(items[0]['gen_male'])+int(items[0]['obc_female'])+int(items[0]['obc_male'])+int(items[0]['pwd_female'])+int(items[0]['pwd_male'])+int(items[0]['sc_female'])+int(items[0]['sc_male'])+int(items[0]['st_female'])+int(items[0]['st_male'])
    else:
        output = "No record found for this year"
        return output
    
    output = "The number of students admitted to the course "+course+" in the year "+batch+" is "+str(total)
    
    clear_session_attributes()
    return output

def adm_query_3(intent, session, batch, gender):
    #batch and gender given
    #how many {gender} students were admitted in the year {batch}
    
    card_title = "Admission Query"
    
    if gender not in possibleGender:
        output = "Sorry, I was not able to process the gender"
        return output
        
    table_name = "Admission_"+batch
    
    course = 'M.Sc. Computer Science'
    table = dynamodb.Table(table_name)
    
    response = table.query(
        KeyConditionExpression=Key('programme').eq(course)  
    )
    if len(response["Items"]) > 0:
        items = response['Items']
        if gender == 'female':
            totalMsc = int(items[0]['gen_female'])+int(items[0]['obc_female'])+int(items[0]['pwd_female'])+int(items[0]['sc_female'])+int(items[0]['st_female'])
        elif gender == 'male':
            totalMsc = int(items[0]['gen_male'])+int(items[0]['obc_male'])+int(items[0]['pwd_male'])+int(items[0]['sc_male'])+int(items[0]['st_male'])
        else:
            output = "I could not process the gender"
            return output
    else:
        output = "No record found for this year"
        return output
        
    course = "MCA"
    response = table.query(
        KeyConditionExpression=Key('programme').eq(course)  
    )
    if len(response["Items"]) > 0:
        items = response['Items']
        if gender == 'female':
            totalMca = int(items[0]['gen_female'])+int(items[0]['obc_female'])+int(items[0]['pwd_female'])+int(items[0]['sc_female'])+int(items[0]['st_female'])
        elif gender == 'male':
            totalMca = int(items[0]['gen_male'])+int(items[0]['obc_male'])+int(items[0]['pwd_male'])+int(items[0]['sc_male'])+int(items[0]['st_male'])
        else:
            output = "I could not process the gender"
            return output
    else:
        output = "No record found for this year"
        return output
        
    course = "PhD"
    response = table.query(
        KeyConditionExpression=Key('programme').eq(course)  
    )
    if len(response["Items"]) > 0:
        items = response['Items']
        if gender == 'female':
            totalPhd = int(items[0]['gen_female'])+int(items[0]['obc_female'])+int(items[0]['pwd_female'])+int(items[0]['sc_female'])+int(items[0]['st_female'])
        elif gender == 'male':
            totalPhd = int(items[0]['gen_male'])+int(items[0]['obc_male'])+int(items[0]['pwd_male'])+int(items[0]['sc_male'])+int(items[0]['st_male'])
        else:
            output = "I could not process the gender"
            return output
    else:
        output = "No record found for this year"
        return output
        
    totalStudents = totalMsc+totalMca+totalPhd
    output = "The number of "+gender+" students admitted in the year "+batch+" is "+str(totalStudents)
   
    clear_session_attributes()
    return output

def adm_query_4(intent, session, batch, gender, course):
    #gender, course and batch given
    #how many {gender} students were admitted to the course {course} in the year {batch}
    
    card_title = "Admission Query"
    
    if course == 'msc' or course == 'msc computer science' or course == 'MSc':
        course = "M.Sc. Computer Science"
    elif course == 'mca' or course == 'masters in computer applications' or course == 'masters in computer application':
        course = "MCA"
    elif course == 'phd' or course == 'doctrate' or course == 'doctrate in philosophy':
        course = "PhD"
    
    if course not in possibleCourse:
        output = "Sorry, I was not able to process the course."
        return output
        
    table_name = "Admission_"+batch
    
    table = dynamodb.Table(table_name)
    
    response = table.query(
        KeyConditionExpression=Key('programme').eq(course)  
    )
    if len(response["Items"]) > 0:
        items = response['Items']
        if gender == 'female':
            total = int(items[0]['gen_female'])+int(items[0]['obc_female'])+int(items[0]['pwd_female'])+int(items[0]['sc_female'])+int(items[0]['st_female'])
        elif gender == 'male':
            total = int(items[0]['gen_male'])+int(items[0]['obc_male'])+int(items[0]['pwd_male'])+int(items[0]['sc_male'])+int(items[0]['st_male'])
        else:
            output = "I could not process the gender"
            return output
    else:
        output = "No record found for this year"
        return output
    
    output = "The number of "+gender+" students admitted in the year "+batch+" is "+str(total)
    
    clear_session_attributes()
    return output

def adm_query_5(intent, session, batch, category):
    #category and batch given
    #how many {category} students were admitted in the year {batch}
    
    card_title = "Admission Query"
    table_name = "Admission_"+batch
    
    if category == 'general':
        maleCol = "gen_male"
        femaleCol = "gen_female"
    elif category == 'obc':
        maleCol = "obc_male"
        femaleCol = "obc_female"
    elif category == 'sc':
        maleCol = "sc_male"
        femaleCol = "sc_female"
    elif category == 'st':
        maleCol = "st_male"
        femaleCol = "st_female"
    elif category == 'pwd':
        maleCol = "pwd_male"
        femaleCol = "pwd_female"
    else:
        output = "Sorry I could not process the category"
        return output
        
    course = 'M.Sc. Computer Science'
    table = dynamodb.Table(table_name)
    
    response = table.query(
        KeyConditionExpression=Key('programme').eq(course)  
    )
    if len(response["Items"]) > 0:
        items = response['Items']
        totalMsc = int(items[0][maleCol])+int(items[0][femaleCol])
    else:
        output = "No record found for this year"
        return output
    
    course = "MCA"
    response = table.query(
        KeyConditionExpression=Key('programme').eq(course)  
    )
    if len(response["Items"]) > 0:
        items = response['Items']
        totalMca = int(items[0][maleCol])+int(items[0][femaleCol])
    else:
        output = "No record found for this year"
        return output
        
    course = "PhD"
    response = table.query(
        KeyConditionExpression=Key('programme').eq(course)  
    )
    if len(response["Items"]) > 0:
        items = response['Items']
        totalPhd = int(items[0][maleCol])+int(items[0][femaleCol])
    else:
        output = "No record found for this year"
        return output
        
    totalStudents = totalMsc+totalMca+totalPhd
    output = "The number of "+category+" students admitted in the year "+batch+" is "+str(totalStudents)
   
    clear_session_attributes()
    return output

def adm_query_6(intent, session, batch, category, course):
    #batch, category and course given
    #how many {category} students were admitted to the course {course} in the year {batch}
    
    card_title = "Admission Query"
    table_name = "Admission_"+batch
    
    if category == 'general':
        maleCol = "gen_male"
        femaleCol = "gen_female"
    elif category == 'obc':
        maleCol = "obc_male"
        femaleCol = "obc_female"
    elif category == 'sc':
        maleCol = "sc_male"
        femaleCol = "sc_female"
    elif category == 'st':
        maleCol = "st_male"
        femaleCol = "st_female"
    elif category == 'pwd':
        maleCol = "pwd_male"
        femaleCol = "pwd_female"
    else:
        output = "Sorry I could not process the category"
        return output
        
    if course == 'msc' or course == 'msc computer science' or course == 'MSc':
        course = "M.Sc. Computer Science"
    elif course == 'mca' or course == 'masters in computer applications' or course == 'masters in computer application':
        course = "MCA"
    elif course == 'phd' or course == 'doctrate' or course == 'doctrate in philosophy':
        course = "PhD"
        
    if course not in possibleCourse:
        output = "Sorry, I was not able to process the course."
        return output

    table = dynamodb.Table(table_name)
    
    response = table.query(
        KeyConditionExpression=Key('programme').eq(course)  
    )
    if len(response["Items"]) > 0:
        items = response['Items']
        total = int(items[0][maleCol])+int(items[0][femaleCol])
    else:
        output = "No record found for this year"
        return output
        
    output = "The number of "+category+" students admitted to the course "+course+" in the year "+batch+" is "+str(total)
   
    clear_session_attributes()
    return output
    
def adm_query_7(intent, session, batch, category, gender):
    #category, gender and batch given
    #how many {category}{gender} were admitted in the year {batch}
    
    card_title = "Admission Query"
    table_name = "Admission_"+batch
    
    if gender not in possibleGender:
        output = "Sorry I was not able to process the gender."
        return output
    
    if category == 'general':
        column = "gen_"+gender
    elif category == 'obc':
        column = "obc_"+gender
    elif category == 'sc':
        column = "sc_"+gender
    elif category == 'st':
        column = "st_"+gender
    elif category == 'pwd':
        column = "pwd_"+gender
    else:
        output = "Sorry I could not process the category"
        return output
        
    course = 'M.Sc. Computer Science'
    table = dynamodb.Table(table_name)
    
    response = table.query(
        KeyConditionExpression=Key('programme').eq(course)  
    )
    if len(response["Items"]) > 0:
        items = response['Items']
        totalMsc = int(items[0][column])
    else:
        output = "No record found for this year"
        return output
    
    course = "MCA"
    response = table.query(
        KeyConditionExpression=Key('programme').eq(course)  
    )
    if len(response["Items"]) > 0:
        items = response['Items']
        totalMca = int(items[0][column])
    else:
        output = "No record found for this year"
        return output
        
    course = "PhD"
    response = table.query(
        KeyConditionExpression=Key('programme').eq(course)  
    )
    if len(response["Items"]) > 0:
        items = response['Items']
        totalPhd = int(items[0][column])
    else:
        output = "No record found for this year"
        return output
        
    totalStudents = totalMsc+totalMca+totalPhd
    output = "The number of "+category+" " +gender+" students admitted in the year "+batch+" is "+str(totalStudents)
   
    clear_session_attributes()
    return output

def adm_query_8(intent, session, batch, category, gender, course):
    #category, gender, course and batch given
    #how many {category}{gender} students were admitted in the course {course} in the year {batch}
    
    card_title = "Admission Query"
    table_name = "Admission_"+batch
    
    if gender not in possibleGender:
        output = "Sorry, I was not able to process the gender."
        return output
    
    if category == 'general':
        column = "gen_"+gender
    elif category == 'obc':
        column = "obc_"+gender
    elif category == 'sc':
        column = "sc_"+gender
    elif category == 'st':
        column = "st_"+gender
    elif category == 'pwd':
        column = "pwd_"+gender
    else:
        output = "Sorry I could not process the category"
        return output
        
    if course == 'msc' or course == 'msc computer science' or course == 'MSc':
        course = "M.Sc. Computer Science"
    elif course == 'mca' or course == 'masters in computer applications' or course == 'masters in computer application':
        course = "MCA"
    elif course == 'phd' or course == 'doctrate' or course == 'doctrate in philosophy':
        course = "PhD"
        
    if course not in possibleCourse:
        output = "Sorry, I was not able to process the course."
        return output
        
    table = dynamodb.Table(table_name)
    
    response = table.query(
        KeyConditionExpression=Key('programme').eq(course)  
    )
    if len(response["Items"]) > 0:
        items = response['Items']
        total = int(items[0][column])
    else:
        output = "No record found for this year"
        return output
        
    output = "The number of "+category+" "+gender+" students admitted to the course "+course+" in the year "+batch+" is "+str(total)
   
    clear_session_attributes()
    return output

def admission(intent, session):
    
    card_title = "Admission"
    intent_name = intent['name']

    existsCourse = False
    existsBatch = False
    existsCategory = False
    existsGender = False
    
    if is_in_intent(intent,'course'):
        course = intent['slots']['course']['value']
        existsCourse = True
        session_attributes['course'] = course
    
    if is_in_intent(intent,'batch'):
        batch = intent['slots']['batch']['value']
        existsBatch = True
        session_attributes['batch'] = batch
    
    if is_in_intent(intent,'category'):
        category = intent['slots']['category']['value']
        existsCategory = True
        session_attributes['category'] = category
        
    if is_in_intent(intent,'gender'):
        gender = intent['slots']['gender']['value']
        existsGender = True
        session_attributes['gender'] = gender
        
    reprompt_text = ""
    
    if not existsBatch:
        #we need batch
        speech_output = "Hey! I found a catch! You forgot the batch!"
        reprompt_text = "What batch information do you need?"
        return build_response(session_attributes, build_dialog_elicit_speechlet("batch", intent, card_title, speech_output, reprompt_text))
    
    if not existsCategory and not existsGender and not existsCourse:
        output = adm_query_1(intent, session, batch)
    elif not existsCategory and not existsGender and existsCourse:
        output = adm_query_2(intent, session, batch, course)
    elif not existsCategory and existsGender and not existsCourse:
        output = adm_query_3(intent, session, batch, gender)
    elif not existsCategory and existsGender and existsCourse:
        output = adm_query_4(intent, session, batch, gender, course)
    elif existsCategory and not existsGender and not existsCourse:
        output = adm_query_5(intent, session, batch, category)
    elif existsCategory and not existsGender and existsCourse:
        output = adm_query_6(intent, session, batch, category, course)
    elif existsCategory and existsGender and not existsCourse:
        output = adm_query_7(intent, session, batch, category, gender)
    elif existsCategory and existsGender and existsCourse:
        output = adm_query_8(intent, session, batch, category, gender, course)
    else:
        #cant help ya
        speech_output = "cant help ya"
       
    clear_session_attributes()
    intent = clear_slot_variables
    speech_output = output
    reprompt_text = speech_output
    
    should_end_session = False
    return build_response({}, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

# ---------------------------------------------- admission queries end ------------------------------------------------- #

# ---------------------------------------------- basic queries begin --------------------------------------------------- #

def dataAvailable(intent, session):
    
    card_title = "Basic Query"
    intent_name = intent['name']
        
    output = ""
    clear_session_attributes()
    speech_output = output
    reprompt_text = speech_output
    
    should_end_session = False
    return build_response({}, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def admProc(intent, session):
    
    card_title = "Basic Query"
    intent_name = intent['name']

    output = ""

    clear_session_attributes()
    speech_output = output
    reprompt_text = speech_output
    
    should_end_session = False
    return build_response({}, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))


def capacity(intent, session):
    
    card_title = "Basic Query"
    intent_name = intent['name']
        
    output = ""

    clear_session_attributes()
    speech_output = output
    reprompt_text = speech_output
    
    should_end_session = False
    return build_response({}, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def coursesDept(intent, session):
    
    card_title = "Basic Query"
    intent_name = intent['name']

    output = "The department of computer science offers the following courses - MSC Computer Science, Masters in computer applications that is MCA and PHD."
    
    clear_session_attributes()
    speech_output = output
    reprompt_text = speech_output
    
    should_end_session = False
    return build_response({}, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
    
def placementTeam(intent, session):
    
    card_title = "Basic Query"
    intent_name = intent['name']

    output = "The department have a faculty placement advisor and each year 6 students are selected as placement coordinators. 3 from MCA and 3 from MSC. " +\
            "A few companies that visit the department for recruitement are - Adobe, Aricent, Cadence, Capgemini, Deloitte, Drishti, Global Logic, HCL, IBM, " +\
            "Infogain, Make My Trip, Mcafee, Microsoft, Nagarro, Snapdeal, TCS, Tech Mahindra, Thoroughgood, Wipro and many more!"
    
    clear_session_attributes()
    speech_output = output
    reprompt_text = speech_output
    
    should_end_session = False
    return build_response({}, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
    
def placement(intent, session):
    
    card_title = "Basic Query"
    intent_name = intent['name']

    output = "The placement record for the department has been phenomenal over the past years. " +\
            "A lot of companies visit the department for recruitement. A few companies that visit the department for recruitement are - Adobe, Aricent, Cadence, Capgemini, Deloitte, Drishti, Global Logic, HCL, IBM, " +\
            "Infogain, Make My Trip, Mcafee, Microsoft, Nagarro, Snapdeal, TCS, Tech Mahindra, Thoroughgood, Wipro and many more!"
    
    clear_session_attributes()
    speech_output = output
    reprompt_text = speech_output
    
    should_end_session = False
    return build_response({}, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

# ---------------------------------------------- basic queries end ----------------------------------------------------- #

def get_help_response():
    
    card_title = "Help"
    
    speech_output = "Hello user! This ia a skill to provide you with any admission related or result related or any other general query related with the department of computer science of university of delhi, DUCS, in short. "+\
                    "Simply ask anything you want to know about DUCS. The available admission queries are - list of available courses in DUCS, the admission procedure for each course, to know how many students were admitted in a particular year, " +\
                    "number of seats available in each course, and many more. While of result, the available queries are - result of a particular student, result of batch, comparison of results, information of topper, and many more! " +|
                    "Other general queries include information about the placements! Whatever you want to know, ask away!"
    reprompt_text = speech_output
    
    should_end_session = False
    
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():

    card_title = "Session Ended"
    speech_output = "Glad I could help. See you again soon!"
    
    should_end_session = True
    
    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))
    
    
def handle_wrong_input():
    
    card_title = "Oops"
    
    speech_output = "you seem to have provided wrong query format. you can always ask for help, or try again"
    reprompt_text = "Oops, wrong input!"
    
    should_end_session = False
    
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
    

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    session_attributes = {}
    

def on_launch(launch_request, session):
    return get_welcome_response()


def on_intent(intent_request, session):
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    
    if intent_name == "ResultIntent":
        return result(intent, session)
    elif intent_name == "AdmissionIntent":
        return admission(intent, session)
    elif intent_name == "capacityIntent":
        return capacity(intent, session)
    elif intent_name == "admissionProcedure":
        return admProc(intent, session)
    elif intent_name == "dataOfYear":
        return dataAvailable(intent, session)
    elif intent_name == "courseInDept":
        return coursesDept(intent, session)
    elif intent_name == "placementTeam":
        return placementTeam(intent, session)
    elif intent_name == "placement":
        return placement(intent, session)

    elif intent_name == "AMAZON.HelpIntent":
        return get_help_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        return handle_wrong_input()
        
def on_session_ended(session_ended_request, session):
    session_attributes = {}

# --------------- Main handler ------------------

session_attributes = {}

def lambda_handler(event, context):
    
    if event['session']['new']:
	    on_session_started({'requestId': event['request']['requestId']},event['session'])
		
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

