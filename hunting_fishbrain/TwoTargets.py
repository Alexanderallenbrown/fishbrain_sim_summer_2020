import random
import math
import time
from HybridFishBrain import FishState


class TwoTargets:
    def __init__(self,ITI_mean,ITI_random,Trial_mean,Trial_random,tleftPose,trightPose):
        #properties
        self.ITI_mean = ITI_mean
        self.ITI_random = ITI_random
        self.Trial_mean = Trial_mean
        self.Trial_random = Trial_random
        self.tleftPose = tleftPose
        self.trightPose = trightPose
        #timers
        self.startTime = time.time()
        self.currTime = time.time()-self.startTime
        self.duration = self.ITI_mean + random.randint(-self.ITI_random,self.ITI_random)
        #pose to send outward
        self.tleftPose = tleftPose
        self.trightPose = trightPose
        self.pose = tleftPose
        
        #trial block info
        #CL control left, EL experimental left (hunts)
        self.trialTypes = ['CR','CL','ER','EL']
        random.shuffle(self.trialTypes)

        self.trial_ind = 0
        self.trialType = self.trialTypes[self.trial_ind]
        
        #state machine. Wait always precedes target.
        self.state = 'wait'
        self.block = 0
        self.hunt = False
    
    def update(self,shot):
        self.trialType = self.trialTypes[self.trial_ind]
        self.currTime = time.time()
        self.elapsed = self.currTime-self.startTime
        #start state machine logic
        if((self.elapsed>self.duration) or shot):
            if(self.state=="wait"):
                if(not shot):
                    newstate = "target"
                    self.startTime = time.time()
                    self.elapsed = 0
                    self.duration = self.Trial_mean + random.randint(-self.Trial_random,self.Trial_random)
                else:
                    pass
            else:
                newstate = "wait"
                self.trial_ind+=1
                self.elapsed = 0
                self.startTime = time.time()
                self.duration = self.ITI_mean + random.randint(-self.ITI_random,self.ITI_random)
                if(self.trial_ind)>=3:
                    self.trial_ind=0
                    random.shuffle(self.trialTypes)
                    self.block+=1
            self.state = newstate
        #now do outputs
        self.hunt = ((self.state=="target") and ((self.trialTypes[self.trial_ind] != ("CR")) and (self.trialTypes[self.trial_ind] != ("CL"))))
        if((self.trialTypes[self.trial_ind]=="CL") or (self.trialTypes[self.trial_ind]=="EL")):
            self.pose = self.tleftPose
        else:
            self.pose = self.trightPose
        
        return self.hunt, self.pose, self.state, self.block
        
        
        
    def newBlock(self):
        #create new order
        self.trialTypes = random.shuffle(self.trialTypes)
        
    
        