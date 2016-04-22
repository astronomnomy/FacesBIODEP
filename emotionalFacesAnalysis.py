from emotionalfaces import *

###################################################

################## dictionaries ###################
#pptnumber : study arm
# study arms:
# 1: control no treatment
# 2: HAM-D < 7 on medication
# 3: HAM-D > 13 on medication
# 4: HAM-D > 17 no medication
studyArmDict={
                '100':1,
                '5004':1,
                '5005':1,
                '5006':1,
            }

###################################################
###################################################
###################################################
###################################################
###################################################
###################################################
###################################################


#.txt file with all the .mat full path names that are being analysed.
# OR use every .mat file in a directory

matfiles="/Users/cc401/data/TH2/Oxford/task/faces/filelist.txt"
matfilesDir="/Users/cc401/data/TH2/Oxford/task/faces/"


#theStudy=makeNewStudyFromFileNamelist('BIODEP', matfiles, studyArmDict)
theStudy=makeNewStudyFromDirectory('BIODEP', matfilesDir, studyArmDict)


####### TO GET THE TIMES OUT FOR THE STUDY ########
#SOME EXAMPLES
trialTypeWanted='happy'
pptWanted='5004'
sessionWanted='1'
thisSession=theStudy.ppts[pptWanted].sessions[sessionWanted]

print "time all stimulus shown"
timesAllStimulusShown = getTimeStimulusShown(thisSession, 'all')
print timesAllStimulusShown

print "time "+trialTypeWanted+" stimulus shown"
timesSomeStimulusShown = getTimeStimulusShown(thisSession, trialTypeWanted)
print timesSomeStimulusShown

#print thisSession.trialType





