from random import random,gauss
import math
import time


class TankBounds:
    def __init__(self,xmin=0,xmax=.75,ymin=0,ymax=.3,zmin=0,zmax=.3):
        self.xmin=xmin
        self.xmax=xmax
        self.ymin=ymin
        self.ymax=ymax
        self.zmin=zmin
        self.zmax=zmax

class FishState():
    def __init__(self,x=0.3,y=0.15,z=0.05,tilt=.5,psi=math.pi,U = 0, Psidot =0, Tiltdot = 0,zdot = 0):
        self.x=x
        self.y=y
        self.z = z
        self.tilt = tilt
        self.psi = psi
        self.U = U
        self.Psidot = Psidot
        self.Tiltdot = Tiltdot
        self.zdot = zdot

class ControllerErrors:
    def __init__(self,e_dist=1000,e_z=1000,e_tilt=1000,e_psi=1000):
        self.e_dist = e_dist
        self.e_z = e_z
        self.e_tilt = e_tilt
        self.e_psi = e_psi

class ControllerInputs:
    def __init__(self,u_U=0,u_z=0,u_tilt=0,u_psi=0):
        self.u_U = u_U
        self.u_z = u_z
        self.u_tilt = u_tilt
        self.u_psi = u_psi

#markov chain in fishbrain only has states swim and coast. Trip out of this is deterministic (signal to hunt)
# transition matrix defined as: https://en.wikipedia.org/wiki/Stochastic_matrix representing probability of TRANSITION i->j
class FishBrain:
    def __init__(self,TranMat=[[.95,.05],[.1,.9]],dT = 0.1):
        #states: swim, coast, huntswim, huntrise, hunttilt, huntcapture
        self.lastTime = 0
        self.wasHunting = False
        self.TranMat = TranMat
        self.state = "swim"
        self.dT = dT
        self.edist_thresh = 0.005
        self.epsi_thresh = 0.01
        self.etilt_thresh = 0.01
        self.ez_thresh = 0.005
        self.complete = False
        

    def update(self,hunt,controller_error,timenow):
        #timenow will tell us whether to really do a state machine update given our Markov update rate
        #hunt is a boolean that tells the fish whether the target is out or not (can delay, but do it outside!!)
        #controller_errors is a list of errors from hunt goals. There are 4 hunt goals:
        if ((timenow - self.lastTime)>=self.dT):
            if ((not hunt) or self.complete):
                if self.wasHunting:
                    self.state = "swim"
                #roll the dice
                roll = random()
                if(self.state=="swim"):
                    if ((roll>(self.TranMat[0][0])) and (roll<=(self.TranMat[0][1]+self.TranMat[0][0]))):
                        newstate = "coast"
                    else:
                        newstate = self.state
                elif(self.state=="coast"):
                    if ((roll>(self.TranMat[1][1])) and (roll<=(self.TranMat[1][1]+self.TranMat[1][0]))):
                        newstate = "swim"
                    else:
                        newstate = self.state
            elif (hunt and self.wasHunting and not self.complete):
                if(self.state=="huntswim"):
                    if(abs(controller_error.e_dist)<=self.edist_thresh):
                        newstate = "huntrise"
                    else:
                        newstate = self.state
                elif(self.state=="huntrise"):
                    if(abs(controller_error.e_z)<=self.ez_thresh):
                        newstate="hunttilt"
                    else:
                        newstate = self.state
                elif(self.state=="hunttilt"):
                    if(abs(controller_error.e_tilt)<=self.etilt_thresh):
                        newstate = "huntcapture"
                    else:
                        newstate = self.state
                elif(self.state=="huntcapture"):
                    if(abs(controller_error.e_dist)<=self.edist_thresh):
                        newstate = "swim"
                        self.complete = True
                    else:
                        newstate = self.state
            else:
                #tell the brain that we are not done hunting
                self.complete = False
                newstate = "huntswim"
            #save last dice roll time
            self.lastTime = timenow
            #actually set new state
            self.state = newstate
        #save old value of hunt update
        self.wasHunting = hunt
        #actually return the state of the brain to be used in other object/function calls.
        return self.state


class PTWSwimController:
    def __init__(self,muu=0.02,muw=0.00,muz = 0.0, nu=.003,nw=.02, nz = 0.005,tauu=0.5,tauw = 0.1,tauz = .5):
        self.muu = muu
        self.muw = muw
        self.muz = muz
        self.nu = nu
        self.nw = nw
        self.nz = nz
        self.tauu = tauu
        self.tauw = tauw
        self.tauz = tauz
        self.oldtime = 0
        #initialize a fish state for calculating old velocity
        self.fishstate_old = FishState()
        self.currspeed = 0
        self.currpsidot = 0
        self.currzdot = 0
    def getControl(self,fishstate,timenow):
        dT = timenow-self.oldtime
        self.oldtime = timenow
        if(dT<=0):
            dT=0.01
        self.currzdot = fishstate.zdot#(fishstate.z-self.fishstate_old.z)/dT
        self.currspeed = fishstate.U#((fishstate.x-self.fishstate_old.x)**2+(fishstate.y-self.fishstate_old.y)**2)**.5
        self.currpsidot = fishstate.Psidot#(fishstate.psi-self.fishstate_old.psi)/dT

        self.currzdot += dT/self.tauz*(self.muz-self.currzdot)+gauss(0,self.nz)
        self.currspeed += dT/self.tauu*(self.muu-self.currspeed)+gauss(0,self.nu)
        self.currpsidot += dT/self.tauw*(self.muw-self.currpsidot)+gauss(0,self.nw)
        u = ControllerInputs()
        u.u_U = self.currspeed
        u.u_z = self.currzdot
        u.u_psi = self.currpsidot
        self.fishstate_old = fishstate

        return u,ControllerErrors()





class DeterministicSwimController:
    def __init__(self,Kpspeed=.1,Kppsi=.1,Kptilt=.1,Kpz = 0.1):
        self.Kpspeed = Kpspeed
        self.Kppsi = Kppsi
        self.Kptilt = Kptilt
        self.Kpz = Kpz

    def getControl(self,goal,fishstate):
        error = ControllerErrors()
        u = ControllerInputs()
        error.e_dist = ((fishstate.x-self.goal.x)**2 + (fishstate.y-self.goal.y)**2)**.5
        error.e_z = goal.z-fishstate.z
        error.e_tilt = goal.tilst-fishstate.tilt
        error.e_psi = goal.psi - fishstate.psi
        u.u_U = self.Kpspeed*error.e_dist
        u.u_z = self.Kpz*error.e_z
        u.u_tilt = self.Kptilt*error.e_tilt
        u.u_psi = self.Kppsi*error.e_psi
        return u,error






class FishControlManager:
    def __init__(self,goals = [FishState(),FishState(),FishState(),FishState()],sc = PTWSwimController(),cc = PTWSwimController(),hsc = DeterministicSwimController(),hrc = DeterministicSwimController(),htc = DeterministicSwimController(),hcc=DeterministicSwimController(),TankBounds = [0,.6,0,.3,-.3,0]):
        self.sc = sc
        self.cc = cc
        self.hsc = hsc
        self.htc = htc
        self.hcc = hcc
        self.hrc = hrc
        self.control_inputs = ControllerInputs()
        self.control_inputs = ControllerErrors()
        self.robotcommand = FishState()
        self.fishstate_old = FishState()
        self.oldtime = 0
        self.goals = goals
        self.TankBounds = TankBounds

    def getControl(self,brainstate,fishstate,timenow):
        
        #format for these is [U phidot psidot]
        #fishstate is [X Y Z phi psi], used for computing control inputs
        if(brainstate == "swim"):
            u,e = self.sc.getControl(fishstate,timenow)
        elif(brainstate == "coast"):
            u,e = self.cc.getControl(fishstate,timenow)
        elif(brainstate == "huntswim"):
            goal = self.goals[0]
            u,e = self.hsc.getControl(goal,fishstate)
        elif(brainstate == "huntrise"):
            goal = self.goals[1]
            u,e = self.hsc.getControl(goal,fishstate)
        elif(brainstate == "hunttilt"):
            goal = self.goals[2]
            u,e = self.htc.getControl(goal,fishstate)
        elif(brainstate == "huntcapture"):
            goal = self.goals[3]
            u,e = self.hcc.getControl(goal,fishstate)
        else:
            print("no valid brain state! from controllermanager")
        
        self.control_inputs = u
        self.controller_error = e
        self.fishstate_old = fishstate
        return u,e

    def getGantryCommand(self,brainstate,fishstate,timenow):
        #compute planar speed
        dt = timenow-self.oldtime
        if(dt<=0):
            dt=.001
            print("trouble with dt! from controller")
        self.oldtime = timenow
        uplanar = ((fishstate.x-self.fishstate_old.x)**2+(fishstate.y-self.fishstate_old.y)**2)**.5/dt
        uz = (fishstate.z-self.fishstate_old.z)/dt
        #fishstate.U = uplanar
        #fishstate.zdot = uz


        self.control_inputs,error = self.getControl(brainstate,fishstate,timenow)
        # fishstate.U = self.control_inputs.u_U
        # fishstate.Psidot = self.control_inputs.u_psi
        # fishstate.Tiltdot = self.control_inputs.u_tilt
        
        #only update if the robot isn't running into a wall.
        if(not (((self.robotcommand.x>=self.TankBounds[1]) and (self.control_inputs.u_U*cos(self.robotcommand.psi)>0)) or ((self.robotcommand.x<=self.TankBounds[0]) and (self.control_inputs.u_U*cos(self.robotcommand.psi)<0)))):
            self.robotcommand.x += dt*(self.control_inputs.u_U*cos(fishstate.psi))

            
        if(not (((self.robotcommand.y>=self.TankBounds[3]) and (self.control_inputs.u_U*sin(self.robotcommand.psi)>0)) or ((self.robotcommand.y<=self.TankBounds[2]) and (self.control_inputs.u_U*sin(self.robotcommand.psi)<0)))):
            self.robotcommand.y += dt*(self.control_inputs.u_U*sin(fishstate.psi))

        if(not (((self.robotcommand.z>=self.TankBounds[5]) and (self.control_inputs.u_z>0)) or ((self.robotcommand.z<=self.TankBounds[4]) and (self.control_inputs.u_z<0)))):
            self.robotcommand.z += dt*(self.control_inputs.u_z)
        if(brainstate == ("swim" or "huntswim" or "huntcapture" or "coast")):
            self.robotcommand.tilt = atan2(uz,uplanar)
        else:
            self.robotcommand.tilt += dt*(self.control_inputs.u_tilt)
        self.robotcommand.psi += dt*(self.control_inputs.u_psi)

        self.robotcommand.U = self.control_inputs.u_U
        self.robotcommand.Psidot = self.control_inputs.u_psi
        self.robotcommand.Tiltdot = self.control_inputs.u_tilt
        
        if( ((self.robotcommand.y>=self.TankBounds[3]) ) ):
            self.robotcommand.y=self.TankBounds[3]
            self.robotcommand.U = uplanar
        if( (self.robotcommand.y<=self.TankBounds[2]) ):
            self.robotcommand.y = self.TankBounds[2]
            self.robotcommand.U = uplanar
        if ((self.robotcommand.x>=self.TankBounds[1])):
            self.robotcommand.x = self.TankBounds[1]
            self.robotcommand.U = uplanar
        if ( (self.robotcommand.x<=self.TankBounds[0])):
            self.robotcommand.x = self.TankBounds[0]
            self.robotcommand.U = uplanar
        if(self.robotcommand.z>=self.TankBounds[5]):
            self.robotcommand.zdot = uz
            self.robotcommand.z=self.TankBounds[5]
        if(self.robotcommand.z<=self.TankBounds[4]):
            self.robotcommand.zdot = uz
            self.robotcommand.z = self.TankBounds[4]

        return self.robotcommand,self.control_inputs,self.controller_error

