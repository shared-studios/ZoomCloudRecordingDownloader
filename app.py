import requests
import json
import os
import urllib2

#keeping our api key and api secret off the program file so it's secure
fl = open('api.txt', 'r')
apis = fl.readlines() 

#print apis

apiKey =  apis[0].replace("\n","")
apiSec =  apis[1].replace("\n","")

#this is defined to make sure no illegal character appear in potential filenames
def correctFileName(filename):
    ret = filename.lower()
    illegalFirstChars = [' ','.','_','-']
    illegalChars = ['#','%','&','{','}','\\','<','>','*','?','/',' ','$','!',"'",'"',':','@']
    for first in illegalFirstChars:
        if ret[0] == first:
            ret = ret[1:]
    for char in illegalChars:
        ret = ret.replace(char,"")
    return ret

#first set of parameters passed to api call
userlistparam = {'api_key': apiKey, 'api_secret': apiSec , 'data_type': "JSON", 'page_size': 300}

#call to retrieve json object containing list of zoom users
userlistjson = requests.post('https://api.zoom.us/v1/user/list', params=userlistparam).json()
users =  userlistjson['users']

#print len(users)
#for i in range(10):

#for loop to go through each user in the list
for i in range(len(users)):

    #this retireves user that is currently being looked at and relevant info
    currUser = users[i]
    #if user has any recordings, this string will be the name of created directory
    username = currUser['email'][:currUser['email'].find('@')]
    #user id needed to pass to api call
    currID = currUser['id']

    #second set of parameters passed to second api call
    videolistparams = {'api_key': apiKey, 'api_secret': apiSec, 'data_type': "JSON", 'host_id': currID, 'page_size': 300}

    #call to retrieve json object cotaining list of user recordings
    videolistjson = requests.post("https://api.zoom.us/v1/recording/list", params=videolistparams).json()
    currUserMeetings = videolistjson['meetings'] 

    #if there user has any recordings, this block of code will download them
    if (len(currUserMeetings) > 0):
        
        if not os.path.exists("./" + username):
            os.makedirs("./" + username)
        print username
        print " "
        for j in range(len(currUserMeetings)):
            currMeeting = currUserMeetings[j]
            #print currMeeting
            meetingName = currMeeting['topic'] + "-" + currMeeting['start_time']
            meetingName = correctFileName(meetingName)
            #print meetingName
            for k in range(len(currMeeting['recording_files'])): 
                currRecording = currMeeting['recording_files'][k]
                if currRecording['file_type'] != 'MP4':
                    continue
                filename = meetingName + '-' + str(k+1) + '.' + currRecording['file_type']
                import urllib2

                url = currRecording['download_url']
                
                u = urllib2.urlopen(url)
                f = open("./" + username + "/" + filename, 'wb')
                meta = u.info()
                file_size = int(meta.getheaders("Content-Length")[0])
                print "Downloading: %s Bytes: %s" % (filename, file_size)
                
                file_size_dl = 0
                block_sz = 8192
                while True:
                    buffer = u.read(block_sz)
                    if not buffer:
                        break
                    
                    file_size_dl += len(buffer)
                    f.write(buffer)
                    status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
                    status = status + chr(8)*(len(status)+1)
                    print status,

                f.close()
                
                #print filename
                
        
        #print username