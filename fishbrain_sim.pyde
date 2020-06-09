from random import random,gauss
from HybridFishBrain import TankBounds,FishState,ControllerErrors,ControllerInputs,FishBrain,PTWSwimController,DeterministicSwimController,FishControlManager
from simGantry import SimGantry
from math import pi
from drawfuncs import TankVizTop,TankVizFront,Button


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
sc = PTWSwimController(muu=0.02,muw=0.1,muz = 0.0, nu=.01,nw=.5, nz = 0.05,tauu=0.1,tauw = .1,tauz = .1)
cc = PTWSwimController(muu=0.0,muw=0.0,muz = 0.0, nu=0,nw=0, nz = 0,tauu=0.1,tauw = .1,tauz = .1)

goals = [goal1,goal2,goal3,goal4]

TankBounds =[0,1,0,.3,-.3,0]

brain = FishBrain(TranMat=[[.9,.1],[.05,.95]])
cont = FishControlManager(goals,sc,cc,hsc,hrc,htc,hcc,TankBounds)

gantry = SimGantry()

w = 640
h = 960
tanktop = TankVizTop(75,100,500,TankBounds)
tankfront = TankVizFront(75,400,500,TankBounds)

rtarg = Button(.75*w,300,25,"right target",14,True,'r')

timenow = 0.0


def setup():
    size(w, h)

def draw():
    timenow = millis()/1000.0
    command,u,e = cont.getGantryCommand(brain.state,gantry.state,timenow)
    brain.update(rtarg.state,e,timenow)
    gantry.update(command,timenow)
    
    
    print(brain.state)
    #print(gantry.state.x,gantry.state.y,gantry.state.psi)
    
    background(255)
    tanktop.draw(gantry.state)
    tankfront.draw(gantry.state)
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
    
    rtarg.updateButton()
    