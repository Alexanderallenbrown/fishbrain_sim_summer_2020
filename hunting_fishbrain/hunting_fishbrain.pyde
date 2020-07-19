from random import random,gauss
from HybridFishBrain import TankBounds,FishState,ControllerErrors,ControllerInputs,FishBrain,PTWSwimController,TargetingController,FishControlManager
from simGantry import SimGantry
from math import pi
from drawfuncs import TankVizTop,TankVizFront,Button,TargetVizTop,TargetVizFront
from TwoTargets import TwoTargets

rTarg = FishState(.35,.15,.15,0,0) #the target has no inherent pitch or yaw requirement
lTarg = FishState(.05,.15,.15,0,0)
#twotargets(ITI_mean,ITI_random,Trial_mean,Trial_random,tleftPose,trightPose)
targets = TwoTargets(5,1,10,1,lTarg,rTarg)


#set up goal positions for each action
# goal1 = FishState(.3,.15,-0.1,0,pi)
# goal2 = FishState(.3,.15,-0.02,0,pi)
# goal3 = FishState(.3,.15,-0.02,-0.5,pi)
# goal4 = FishState(.3,.1,-0.02,0,pi)

#these are the goals. They're all target positions but with different heights and tilts
goalTarg = FishState(.85,.15,.15,0,0) #the target has no inherent pitch or yaw requirement

#set up controllers for each state
tc = TargetingController()
# sc = PTWSwimController(muu=0.02,muw=0.1,muz = 0.0, nu=.01,nw=.5, nz = 0.05,tauu=0.1,tauw = .1,tauz = .1)
# cc = PTWSwimController(muu=0.0,muw=0.0,muz = 0.0, nu=0,nw=0, nz = 0,tauu=0.1,tauw = .1,tauz = .1)
# SPENCER PARAMS BELOW

#ACTIVE
sc = PTWSwimController(muu=0.067,muw=0.0057,muz = 0.0, nu=(.0042),nw=(1.509), nz = (0.0025),tauu=3.67,tauw = .5916,tauz = .517)
#INACTIVE
cc = PTWSwimController(muu=0.0162,muw=0,muz = 0.0, nu=0.18,nw=0, nz = 0,tauu=1.0/20,tauw = 1.0/.18,tauz = 1.0/9.64)
goals = goalTarg

TankBounds =[0,.4,0,.15,-.15,0]

# brain = FishBrain(TranMat=[[.9,.1],[.2,.8]])
#spencer params below
brain = FishBrain(TranMat=[[.9585,1-.9585],[1-.9884,.9884]],dT=0.033)
cont = FishControlManager(goals,sc,cc,tc,TankBounds)

gantry = SimGantry()

w = 640
h = 720
tanktop = TankVizTop(200,100,500,TankBounds)
rtarg_viztop = TargetVizTop(200,100,500,.05,goalTarg,TankBounds)
rtarg_vizfront = TargetVizFront(200,400,500,.05,goalTarg,TankBounds)
tankfront = TankVizFront(200,400,500,TankBounds)


rtarg = Button(.55*w,300,25,"right target",14,True,'r')

timenow = 0.0

hunt = False



def setup():
    size(w, h)

def draw():
    
    ##LOGIC AND CONTROL
    
    timenow = millis()/1000.0
    #update the fish controller's target goal
    cont.goal = targets.pose
    #update the fish controller
    command,u,e = cont.getGantryCommand(brain.state,gantry.state,timenow)
    #update fishbrain state
    brainstate, shot = brain.update(targets.hunt,e,timenow)
    #update the robot gantry
    gantry.update(command,timenow)
    #update the target controller
    targets.update(shot)
    
    
    ## DRAWING STUFF
    
    rtarg_viztop.pose = targets.pose
    rtarg_vizfront.pose = targets.pose
    
    
    background(255)
    tanktop.draw(gantry.state,cont.tailangle)
    tankfront.draw(gantry.state)
    if(targets.state=="target"):
        rtarg_viztop.drawTargetTop(cont)
        rtarg_vizfront.drawTargetFront(cont)
    #draw second fish
    stroke(125);
    tanktop.drawFishTop(command)
    tankfront.drawFishFront(command)
        
    stroke(0);
    fill(0);
    textAlign(CENTER);
    strokeWeight(1)
    textSize(24)
    text("Top View Tank",w/2,80)
    text("Front View Tank",w/2,380)
    text("Robot State: "+brain.state,w/2,650)
    textSize(18)
    text("block: " + str(targets.block)+ ", trial type: "+targets.trialType+ ", target state: " + targets.state + ", time: " + "{:.2f}".format(targets.elapsed) + "/" + str(targets.duration),w/2,700)
    
    #rtarg.updateButton()
    
