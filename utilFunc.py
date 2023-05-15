#twitch-dl, ffmpeg, twitchAPI



from pathlib import Path
from twitchAPI import Twitch
import pprint
import os #look into subprocess to run commands
import datetime
import subprocess

#subprocess.run(args = 'pipx install twitchAPI twitch-dl', shell = True, check = True)

def fetchClips(targetChan: str, numClips: int, clipTimeframe: int, appID: str, appSecret: str)-> list[tuple[str, str]]:
    APP_ID = appID
    APP_SECRET = appSecret

    twitch = Twitch(APP_ID, APP_SECRET)


    #call for urls
    targetChannel = targetChan
    numberOfClips = numClips
    clipTimeFrame = -1 * clipTimeframe #how many days in the past to grab clips from

    broadcasterData = twitch.get_users(logins = targetChannel)
    broadID = broadcasterData['data'][0]['id']
    weekPrior = datetime.datetime.today() + datetime.timedelta(days = clipTimeFrame)
    clipData = twitch.get_clips(broadcaster_id = broadID, first = numberOfClips, started_at = weekPrior, ended_at = datetime.datetime.today())
    #pprint.pprint(clipData)

    numberOfClips = len(clipData['data'])
    clipURLS = []
    for i in range(numberOfClips): #numberOfClips
        clipURLS.append(clipData['data'][i]['url'])



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

    clipInfo = []
    for i in range(numberOfClips):
        x = (clipNames[i], clipURLS[i])
        clipInfo.append(x)

    return clipInfo

def downloadClips(numClips: int, clipInfo: list[tuple[str, str]]):
    numberOfClips = numClips
    
    dirPath = '.\\clipFolder\\' + str(datetime.date.today())
    if(not os.path.exists(dirPath)):
        os.makedirs(dirPath)
    os.chdir(dirPath)

    for i in range(numberOfClips):
        print('\n\n\n' + clipInfo[i][1])
        #os.system('twitch-dl download ' + clipURLS[i] + ' --overwrite -q source -o ' + clipNames[i])
        dlCommand = 'twitch-dl download ' + clipInfo[i][1] + ' --overwrite -q source -o ' + clipInfo[i][0]
        subprocess.run(args=dlCommand, shell=True, check=False)
    print("-------------------clips downloaded-------------------")

def resizeClips(clipInfo: list[tuple[str, str]], mode: str):
    clipNames = []
    for i in range(len(clipInfo)):
        clipNames.append(clipInfo[i][0])


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

def combineClips(targetChannel: str, clipInfo: list[tuple[str, str]]):
    clipNames = []
    for i in range(len(clipInfo)):
        clipNames.append(clipInfo[i][0])

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