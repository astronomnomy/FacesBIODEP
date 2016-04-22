from scipy.io import loadmat
import numpy as np
import matplotlib.pyplot as plt
import glob

############### class definitions #################


class RunParams:
    '''A set of run parameters that can be attached to a Session object'''
    def __init__(self,scannerKey,responseKeys1,responseKeys2,seed,startPulseTime,stimuliTime,responseTime,TR=None):

        self.scannerKey=scannerKey
        self.responseKeys1=responseKeys1
        self.responseKeys2=responseKeys2
        self.seed=seed
        self.startPulseTime=startPulseTime
        self.stimuliTime=stimuliTime
        self.responseTime=responseTime
        self.TR = TR #can specify in a function call or not or can access later. This is not by standard recorded in the .mat file.


class Session:
    '''class associated with an individual session'''
    def __init__(self,sessionName,trial,trialType,picture,gender,timeStimPresn,jitterTime,keyTime,key,response,rt,runParams):
        self.sessionName=sessionName
        self.trial=trial
        self.trialType=trialType
        self.picture=picture
        self.gender=gender
        self.timeStimPresn=timeStimPresn
        self.jitterTime=jitterTime
        self.keyTime=keyTime
        self.key = key
        self.response=response
        self.rt=rt
        self.runParams=runParams #get these from the above class

    
    def getHappyTrials(self):
        '''get indices of gain trials in sessions'''
        return np.where(self.trialType == 'h')[0]
    
    def getNeutralTrials(self):
        '''get indices of look trials in sessions.'''
        return np.where(self.trialType == 'n')[0]
    
    def getSadTrials(self):
        '''get indices of loss trials in sessions'''
        return np.where(self.trialType == 's')[0]




class Ppt:
    '''the class associated with an individual participant'''
    def __init__(self, pptName, studyArm, sessions=None):
        self.pptName = pptName
        self.studyArm   = studyArm
        
        self.sessions = {}
        try:
            sessNames=[sessions[i].sessionName for i in len(sessions)]
            self.sessions.update(dict(zip(sessNames, sessions)))
        except:
            self.sessions.update({sessions.sessionName : sessions})


    def __setitem__(self, key, item):
        self.sessions[key]=item
    
    def __getitem__(self, key):
        return self.sessions[key]
    
    def listSessions(self):
        '''returns a list of sessions attached to the participant'''
        return self.sessions.keys()
    
    def addSession(self, session):
        '''add a session to the ppt'''
        self.sessions.__setitem__(session.sessionName,session)



class Study:
    ''' define a study with a name and a list of ppts'''
    def __init__(self, studyName, ppts=None):
        '''declare a new study with participants'''
        self.studyName=studyName
        self.ppts={}
        if ppts is not None:
            try:
                pptNames=[ppts[i].pptName for i in len(ppts)]
                self.ppts.update(dict(zip(pptNames, ppts)))
            except:
                self.ppts.update({ppts.pptName : ppts})




    def __setitem__(self, key, item):
        '''add a new session'''
        self.ppts[key]=item
    
    def __getitem__(self, key):
        '''return a session'''
        return self.ppts[key]
    
    def listPpts(self):
        '''returns a list of ppts attached to the study'''
        return self.ppts.keys()
    
    def addPpt(ppt):
        '''adds an existing participant to a study'''
        self.ppts.__setitem__(ppt.pptName, ppt)
    
    def addNewPpt(self, pptName, studyArm, aSession=None):
        '''makes a new participant and adds to a study'''
        orphanPpt=Ppt(pptName, studyArm, aSession)
        self.ppts.__setitem__(orphanPpt.pptName, orphanPpt)
    


###################################################

############## function definitions ###############
##
def readReturnSession(filename):
    '''
        give .mat file from the RLtask and session number associated with the ppt, returns python object.
        NB trial starts at 1 in matlab but changed to start at trial 0 in python for consistency
        with python indexing.
        '''
    matStruct = loadmat(filename)
    theseRunParams=RunParams(matStruct['SCANNERKEY'][0],matStruct['RESPONSEKEYS1'][0],
                             matStruct['RESPONSEKEYS2'][0], matStruct['seed'][0],
                             matStruct['STARTPULSETIME'][0], matStruct['STIMULITIME'][0],
                             matStruct['RESPONSETIME'][0])
        
        
    sessionName=filename.split('/')[-1].split('.')[0].split('_')[-1][4:]
                             
    matStructData=matStruct['data']
    
    #The gender, emotions and pictures arrays are a complete mess of tuples arrays and unicodes, this fixes this
    emotions = np.array([ str(matStruct['emotions'][0][i][0]) for i in range(len(matStruct['emotions'][0]))])
    genders = np.array([ str(matStruct['genders'][0][i][0]) for i in range(len(matStruct['genders'][0]))])
    pictures = np.array([ str(matStruct['pictures'][0][i][0]) for i in range(len(matStruct['pictures'][0]))])


    
    #NB, trial indexing starts at zero
    theseData=Session(sessionName,matStructData[:,0]-1,emotions,
                      pictures, genders, matStructData[:,2],
                      matStructData[:,3], matStructData[:,4], matStructData[:,5],
                      matStructData[:,6], matStructData[:,7], theseRunParams)
                      
    return theseData

##
def getPptNum(filename):
    '''Given the filename structure used by the RL code, the ppt number is returned as a string'''
    return str(filename.split('/')[-1].split('_')[0])

##

def makeNewStudyFromFileNamelist(studyName, fileNameList, studyArmDict):
    
    '''Given a name for a study, a list of files and a dictionary that matches the pptnumber to a study arm,
        a study object is created that has multiple participant objects, and each of those have associated sessions.
        From this study requests for fitting and averaging over individual sessions or trial types can be made'''
    
    fileList = np.loadtxt(fileNameList,unpack=True,dtype='string')
    
    theStudy=Study(studyName)
    
    for filename in fileList:
        pptNum = getPptNum(filename)
        aSession=readReturnSession(filename)
        
        
        if pptNum in theStudy.ppts:
            print "adding new session ",aSession.sessionName," on existing ppt ",pptNum," to study ",theStudy.studyName
            theStudy.ppts[pptNum].addSession(aSession)
        else:
            print "adding new session ",aSession.sessionName," and new ppt ",pptNum," to study ",theStudy.studyName
            theStudy.addNewPpt(pptNum, studyArmDict[pptNum],aSession)


    return theStudy


##

def makeNewStudyFromDirectory(studyName, fileNameDir, studyArmDict):
    
    '''Given a name for a study, a directory containing files and a dictionary that matches the pptnumber to a study arm,
        a study object is created that has multiple participant objects, and each of those have associated sessions.
        From this study requests for fitting and averaging over individual sessions or trial types can be made'''
    
    fileList = glob.glob(fileNameDir+'*.mat')
    
    theStudy=Study(studyName)
    
    for filename in fileList:
        pptNum = getPptNum(filename)
        aSession=readReturnSession(filename)
        
        
        if pptNum in theStudy.ppts:
            print "adding new session ",aSession.sessionName," on existing ppt ",pptNum," to study ",theStudy.studyName
            theStudy.ppts[pptNum].addSession(aSession)
        else:
            print "adding new session ",aSession.sessionName," and new ppt ",pptNum," to study ",theStudy.studyName
            theStudy.addNewPpt(pptNum, studyArmDict[pptNum],aSession)


    return theStudy



##

def getTimeStimulusShown(thisSession, trialType):
    '''
        given a session and trial type (happy,'h', neutral, 'n', sad, 's') function returns the times in milliseconds from the first real scan
        '''
    
    if trialType == 'happy' or trialType == 'h':
        trials=thisSession.getHappyTrials()
    elif trialType == 'neutral' or trialType == 'n':
        trials=thisSession.getNeutralTrials()
    elif trialType == 'sad' or trialType == 's':
        trials=thisSession.getSadTrials()
    elif trialType == 'all':
        trials=thisSession.trial
    else:
        raise ValueError("choose trialType to be happy, h, neutral, n, or sad, or all")
    
    
    return thisSession.timeStimPresn[trials]





