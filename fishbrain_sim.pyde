from random import random,gauss
from HybridFishBrain import TankBounds,FishState,ControllerErrors,ControllerInputs,FishBrain,PTWSwimController,DeterministicSwimController,FishControlManager
from simGantry import SimGantry
from math import pi


#set up goal positions for each action
goal1 = FishState(.3,.15,-0.1,0,pi)
goal2 = FishState(.3,.15,-0.02,0,pi)
goal3 = FishState(.3,.15,-0.02,-0.5,pi)
goal4 = FishState(.3,.1,-0.02,0,pi)

#set up controllers for each state
hsc = DeterministicSwimController()
hrc = DeterministicSwimController()
htc = DeterministicSwimController()
hcc = DeterministicSwimController()
sc = PTWSwimController()
cc = PTWSwimController(muu=0.0,muw=0.0,muz = 0.0, nu=.03,nw=.1, nz = 0.005,tauu=0.5,tauw = 0.1,tauz = .5)

goals = [goal1,goal2,goal3,goal4]

TankBounds =[0,.6,0,.3,-.3,0]

brain = FishBrain()
cont = FishControlManager(goals,sc,cc,hsc,hrc,htc,hcc,TankBounds)

gantry = SimGantry()

botL = 0.1

simscale = 1000 #pixels per meter

timenow = 0.0


def setup():
    size(480, 120)

def draw():
    timenow = millis()/1000.0
    command,u,e = cont.getGantryCommand(brain.state,gantry.state,timenow)
    brain.update(False,e,timenow)
    gantry.update(command,timenow)
    
    print(brain.state)
    print(gantry.state.x,gantry.state.y,gantry.state.psi)