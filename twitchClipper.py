#todo
    #look into subprocess to run commands
    #check if files exist first, then delete them



#twitch-dl, ffmpeg, twitchAPI, ,simple-youtube-api, MoviePy(not really)
from pathlib import Path
from twitchAPI import Twitch
import pprint
import os #look into subprocess to run commands
import datetime
import subprocess
#from moviepy.editor import *

APP_ID = 'appid'
APP_SECRET = 'appsecret'

twitch = Twitch(APP_ID, APP_SECRET)
#twitch.authenticate_app([])


#call for urls
targetChannel = 'slimeirl'
numberOfClips = 15
clipTimeFrame = -365 #how many days in the past to grab clips from

title = f'Top {targetChannel} clips of the month'
description = 'Thank you for watching! This video is the result of a college student\'s summer project to automate clip videos.'

broadcasterData = twitch.get_users(logins = targetChannel)
broadID = broadcasterData['data'][0]['id']
weekPrior = datetime.datetime.today() + datetime.timedelta(days = clipTimeFrame)
clipData = twitch.get_clips(broadcaster_id = broadID, first = numberOfClips, started_at = weekPrior, ended_at = datetime.datetime.today())
pprint.pprint(clipData)

numberOfClips = len(clipData['data'])
topClips = []
for i in range(numberOfClips): #numberOfClips
    topClips.append(clipData['data'][i]['url'])



#create names for clips
clipNames = []
for i in range(numberOfClips):
    rawName = str(clipData['data'][i]['title'])
    name = ''
    for j in rawName:
        if str(j).isalnum():
            name = name + j
    if name == '':
        name = name + str(i)
    name = name + str('.mp4')
    clipNames.append(name)



#download clips
dirPath = '.\\clipFolder\\' + str(datetime.date.today())
if(not os.path.exists(dirPath)):
    os.makedirs(dirPath)
os.chdir(dirPath)

for i in range(numberOfClips):
    print('\n\n\n' + topClips[i])
    #os.system('twitch-dl download ' + topClips[i] + ' --overwrite -q source -o ' + clipNames[i])
    dlCommand = 'twitch-dl download ' + topClips[i] + ' --overwrite -q source -o ' + clipNames[i]
    subprocess.run(args=dlCommand, shell=True, check=True)
print("-------------------clips downloaded-------------------")


#resize clips to same dimensions
##using ffmpeg
#check for most common resolution, resize all others
def resizeClips(clipNames, mode):

    resCountDict = {} #dictionary of resolutions and quantity of those resolutions
    resDict = {} #dictionary of clipnames and corresponding resolution
    for i in clipNames:
        getResCommand = f'ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0:s=x {i}'
        #getResCommand = f'ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0:s=x surprise.mp4'
        out = subprocess.run(args=getResCommand, capture_output=True, shell=True, check=True)
        tempRes = str(out.stdout)
        tempRes = tempRes[2:(int(tempRes.find('r'))-1)]
        print(tempRes)
        resDict[i] = tempRes
        if(tempRes in resCountDict):
            resCountDict[tempRes] = resCountDict[tempRes] + 1
        else:
            resCountDict[tempRes] = 1

    if mode=='fast':
        #resize all to most common resolution of the batch
        print('fast')
    elif mode == 'HD':
        #resize all to 1920x1080

        for i in clipNames:
            if(resDict[i] != '1920x1080'):
                print("RESIZING CLIP: "+i)
                newClipName = 'RESIZED' + i
                oldClipName = i
                resizeCommand = f'ffmpeg -y -i {i} -vf scale=1920:1080 {newClipName}'
                subprocess.run(args=resizeCommand, shell=True, check=True)
                os.remove(oldClipName)
                os.rename(newClipName, oldClipName)

    elif mode == 'safe':
        # for i in range(len(clipNames)):
        #     newClipName = 'RESIZED' + clipNames[i]
        #     resizeCommand = f'ffmpeg -y -i {clipNames[i]} -vf scale=1920:1080 {newClipName}'
        #     subprocess.run(args=resizeCommand, shell=True, check=True)
        #     os.remove(clipNames[i])
        #     clipNames[i] = newClipName
        for i in clipNames:
            newClipName = 'RESIZED' + i
            oldClipName = i
            resizeCommand = f'ffmpeg -y -i {i} -vf scale=1920:1080 {newClipName}'
            subprocess.run(args=resizeCommand, shell=True, check=True)
            os.remove(oldClipName)
            os.rename(newClipName, oldClipName)

resizeClips(clipNames, mode='safe')

#combine clips and delete old clips
tempClipString = ''
for i in range(len(clipNames)):

    #old resizing code
    # newClipName = 'RESIZED' + clipNames[i]
    # resizeCommand = f'ffmpeg -y -i {clipNames[i]} -vf scale=1920:1080 {newClipName}'
    # subprocess.run(args=resizeCommand, shell=True, check=True)
    # os.remove(clipNames[i])
    # clipNames[i] = newClipName

    tempClipString = tempClipString + 'file ' + clipNames[i] + '\n'
clipPath = Path.cwd() / 'clips.txt'
mergeClipFile = open(clipPath, 'w')
mergeClipFile.write(tempClipString)
mergeClipFile.close()
#os.system(f'ffmpeg -y -f concat -i clips.txt -c copy combinedClips({datetime.date.today()}).mp4')
concCommand = f'ffmpeg -y -f concat -i clips.txt -c copy {targetChannel}CombinedClips({datetime.date.today()}).mp4'
subprocess.run(args=concCommand, shell=True, check=True)
print(clipPath)
print('.\\clipFolder\\' + str(datetime.date.today()))

os.remove("clips.txt")
for i in clipNames:
    if os.path.exists(i):
        os.remove(i)

'''
##using moviepy to combine clips
moviePyClips = []
for i in clipNames:
    tempClip = VideoFileClip(i)
    tempClip = tempClip.resize(newsize = (1920, 1080))
    #tempClip.save_frame(f'clipFrame_{i}.jpeg')
    moviePyClips.append(tempClip)

combinedClips = concatenate_videoclips(moviePyClips)
combinedClips.write_videofile(f'combinedClips-{datetime.date.today()}.mp4', threads = 8)
'''

#upload to youtube


#from simple_youtube_api.Channel import Channel
#from simple_youtube_api.LocalVideo import LocalVideo
#
## loggin into the channel
#channel = Channel()
#os.chdir('..\\..')
#channel.login("client_secret.json", "credentials.storage")
#
## setting up the video that is going to be uploaded
#combinedClipsName = f'combinedClips({datetime.date.today()}).mp4'
#currentDate = str(datetime.date.today())
#video = LocalVideo(file_path=f'.\\clipfolder\\{currentDate}\\{combinedClipsName}')
#
## setting snippet
#video.set_title(title)
#video.set_description(description)
#video.set_tags(["twitch", "clips", "variety", "automated", "python", "gaming"])
#video.set_category("gaming")
#video.set_default_language("en-US")
#
## setting status
#video.set_embeddable(True)
#video.set_license("creativeCommon")
#video.set_privacy_status("unlisted")
#video.set_public_stats_viewable(True)
#
## setting thumbnail
##video.set_thumbnail_path("test_thumb.png")
##video.set_playlist("PLDjcYN-DQyqTeSzCg-54m4stTVyQaJrGi")
#
## uploading video and printing the results
#video = channel.upload_video(video)
#print(video.id)
#print(video)
