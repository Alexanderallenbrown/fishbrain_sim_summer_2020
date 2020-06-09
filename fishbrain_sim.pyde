from random import random,gauss
from HybridFishBrain import TankBounds,FishState,ControllerErrors,ControllerInputs,FishBrain,PTWSwimController,DeterministicSwimController,FishControlManager
from simGantry import SimGantry
from math import pi
from drawfuncs import TankViz


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
sc = PTWSwimController(muu=0.02,muw=0.1,muz = 0.0, nu=.01,nw=.5, nz = 0.005,tauu=0.1,tauw = .1,tauz = .1)
cc = PTWSwimController(muu=0.0,muw=0.0,muz = 0.0, nu=0,nw=0, nz = 0,tauu=0.1,tauw = .1,tauz = .1)

goals = [goal1,goal2,goal3,goal4]

TankBounds =[0,1,0,.3,-.3,0]

brain = FishBrain(TranMat=[[.9,.1],[.05,.95]])
cont = FishControlManager(goals,sc,cc,hsc,hrc,htc,hcc,TankBounds)

gantry = SimGantry()

w = 640
h = 480
tank = TankViz(100,100,500,TankBounds)

timenow = 0.0


def setup():
    size(w, h)

def draw():
    timenow = millis()/1000.0
    command,u,e = cont.getGantryCommand(brain.state,gantry.state,timenow)
    brain.update(False,e,timenow)
    gantry.update(command,timenow)
    
    
    print(brain.state)
    #print(gantry.state.x,gantry.state.y,gantry.state.psi)
    
    background(255)
    tank.draw(gantry.state)
    stroke(125);
    tank.drawFishTop(command)