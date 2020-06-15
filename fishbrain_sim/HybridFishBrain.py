from random import random,gauss
import math
import time

def sign(inp):
    if(inp==0):
        out=0
    else:
        out=abs(inp)/inp
    return out

class TankBounds:
    def __init__(self,xmin=0,xmax=.75,ymin=0,ymax=.3,zmin=0,zmax=.3):
        self.xmin=xmin
        self.xmax=xmax
        self.ymin=ymin
        self.ymax=ymax
        self.zmin=zmin
        self.zmax=zmax

class FishState():
    def __init__(self,x=0.3,y=0.05,z=-0.15,tilt=.5,psi=math.pi,U = 0, Psidot =0, Tiltdot = 0,zdot = 0):
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
    def __init__(self,e_dist=1000,e_z=1000,e_tilt=1000,e_psi=1000,true_dist=1000):
        self.e_dist = e_dist
        self.e_z = e_z
        self.e_tilt = e_tilt
        self.e_psi = e_psi
        self.true_dist = true_dist

class ControllerInputs:
    def __init__(self,u_U=0,u_z=0,u_tilt=0,u_psi=0):
        self.u_U = u_U
        self.u_z = u_z
        self.u_tilt = u_tilt
        self.u_psi = u_psi

#markov chain in fishbrain only has states swim and coast. Trip out of this is deterministic (signal to hunt)
# transition matrix defined as: https://en.wikipedia.org/wiki/Stochastic_matrix representing probability of TRANSITION i->j
class FishBrain:
    def __init__(self,TranMat=[[.95,.05],[.02,.98]],dT = 0.1):
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
            if ((not hunt) or (self.complete and self.wasHunting)):
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
                    if ((roll>(self.TranMat[1][1])) and (roll<=(self.TranMat[1][0]+self.TranMat[1][1]))):
                        newstate = "swim"
                    else:
                        newstate = self.state
            elif (hunt and self.wasHunting and not self.complete):
                if(self.state=="huntswim"):
                    if(abs(controller_error.true_dist)<=self.edist_thresh):
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
            #print(self.state,hunt,self.wasHunting)
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
    def getControl(self,fishstate,dT):
        # dT = timenow-self.oldtime
        # self.oldtime = timenow
        if(dT<=0):
            dT=0.01
        self.currzdot = fishstate.zdot#(fishstate.z-self.fishstate_old.z)/dT
        self.currspeed = fishstate.U#((fishstate.x-self.fishstate_old.x)**2+(fishstate.y-self.fishstate_old.y)**2)**.5
        self.currpsidot = fishstate.Psidot#(fishstate.psi-self.fishstate_old.psi)/dT

        self.currzdot += dT/self.tauz*(self.muz-self.currzdot)+gauss(0,self.nz) + .3*dT/(self.tauz)*(-.15-fishstate.z)
        self.currspeed += dT/self.tauu*(self.muu-self.currspeed)+gauss(0,self.nu)
        self.currpsidot += dT/self.tauw*(self.muw-self.currpsidot)+gauss(0,self.nw)
        u = ControllerInputs()
        
        u.u_U = self.currspeed
        u.u_z = self.currzdot
        u.u_psi = self.currpsidot
        self.fishstate_old = fishstate

        return u,ControllerErrors()


class TargetingController:
    def __init__(self,Kpspeed=2,Kppsi=1.5,Kptilt=1,Kpz = .5,tiltAng = 1.0,shotDepth = 0.0):
        self.Kpspeed = Kpspeed
        self.Kppsi = Kppsi
        self.Kptilt = Kptilt
        self.Kpz = Kpz
        self.tiltAng = tiltAng
        self.shotDepth = shotDepth
        self.Kpv = .05
        self.Kptiltdot = .05
        self.Kppsidot = .75
        self.Kpzdot = .1
        self.ang_err_old = 0

    def getTargetingError(self,goal,fishstate,huntcapture=False):
        #get global x and y 
        Y_err = goal.y-fishstate.y
        X_err = goal.x-fishstate.x
        #find angle between fish CG and target
        goal_ang = math.atan2(Y_err,X_err)
        #print(goal_ang)
        #find x distance in fish's local coordinate system to target
        x_dist = X_err*math.cos(fishstate.psi) + Y_err*math.sin(fishstate.psi)
        #find goal distance based on target height
        
        if( not huntcapture):
            goal_dist = (goal.z-self.shotDepth)/(math.tan(self.tiltAng))
        else:
            goal_dist = 0
        true_dist = goal_dist - ((fishstate.x-goal.x)**2+(fishstate.y-goal.y)**2)**.5
        #sprint(goal_dist)
        
        # if(abs((goal_ang-fishstate.psi))<abs((goal_ang+2*math.pi-fishstate.psi))):
        #     ang_err =   goal_ang*2*math.pi*round(fishstate.psi/(2*math.pi)) - (fishstate.psi)
        # else:
        #     ang_err = goal_ang*round(fishstate.psi/(2*math.pi))*2*math.pi - (fishstate.psi) - math.pi
        goal_ang = 2*math.pi*round(fishstate.psi/(2*math.pi)) + goal_ang
        ang_err = goal_ang-fishstate.psi    
        #print(goal_ang-fishstate.psi)
        x_err = -goal_dist+x_dist
        return x_err,ang_err,true_dist
    
    def getControl(self,goal,fishstate,brainstate,huntcapture=False):
        error = ControllerErrors()
        u = ControllerInputs()
        #use built-in function to get the planar error 
        x_err,ang_err,true_dist = self.getTargetingError(goal,fishstate,huntcapture)
        #this error should be the "local x" error for the fish.
        error.e_dist = x_err
        error.true_dist = true_dist
        if(brainstate=="huntswim"):
            error.e_z=0
        else:
            error.e_z = (self.shotDepth-fishstate.z)
        if(brainstate==("huntswim")  or brainstate==("huntrise")):
            error.e_tilt = 0
        elif(brainstate==("hunttilt")):
            error.e_tilt = -self.tiltAng-fishstate.tilt
        elif(brainstate==("huntcapture")):
            error.e_tilt = 0-fishstate.tilt
            error.e_psi = 0
            
        error.e_psi = ang_err
        
        u.u_U = self.Kpspeed*error.e_dist - self.Kpv*fishstate.U
        if(abs(u.u_U)>.05):
            u.u_U = sign(u.u_U)*.05
            #print("speed limit")
        u.u_z = self.Kpz*error.e_z - self.Kpzdot*fishstate.zdot
        u.u_tilt = self.Kptilt*error.e_tilt - self.Kptiltdot*fishstate.Tiltdot
        u.u_psi = self.Kppsi*error.e_psi -self.Kppsidot*fishstate.Psidot
        return u,error







class FishControlManager:
    def __init__(self,goal = FishState(),sc = PTWSwimController(),cc = PTWSwimController(),tc = TargetingController(),TankBounds = [0,.6,0,.3,-.3,0]):
        self.sc = sc
        self.cc = cc

        self.tc =tc
        self.control_inputs = ControllerInputs()
        self.control_errors = ControllerErrors()
        self.robotcommand = FishState()
        self.fishstate_old = FishState()
        self.oldtime = 0
        self.goal = goal
        self.TankBounds = TankBounds

    def getControl(self,brainstate,fishstate,dt):
        
        #format for these is [U phidot psidot]
        #fishstate is [X Y Z phi psi], used for computing control inputs
        if(brainstate == "swim"):
            u,e = self.sc.getControl(fishstate,dt)
        elif(brainstate == "coast"):
            u,e = self.cc.getControl(fishstate,dt)
        elif((brainstate == "huntswim") or (brainstate == "huntrise") or (brainstate == "hunttilt") ):
            u,e = self.tc.getControl(self.goal,fishstate,brainstate)
        elif((brainstate == "huntcapture")):
            u,e = self.tc.getControl(self.goal,fishstate,brainstate,True)
        else:
            print("brainstate is: "+brainstate)
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
        # uplanar = ((fishstate.x-self.fishstate_old.x)**2+(fishstate.y-self.fishstate_old.y)**2)**.5/dt
        # uz = (fishstate.z-self.fishstate_old.z)/dt
        # #fishstate.U = uplanar
        # #fishstate.zdot = uz


        self.control_inputs,error = self.getControl(brainstate,fishstate,dt)
        # fishstate.U = self.control_inputs.u_U
        # fishstate.Psidot = self.control_inputs.u_psi
        # fishstate.Tiltdot = self.control_inputs.u_tilt
        self.robotcommand.U = self.control_inputs.u_U
        self.robotcommand.Psidot = self.control_inputs.u_psi
        self.robotcommand.Tiltdot = self.control_inputs.u_tilt
        self.robotcommand.zdot = self.control_inputs.u_z
        uplanar = self.control_inputs.u_U
        uz = self.robotcommand.zdot
        
        #only update if the robot isn't running into a wall.
        if(not (((self.robotcommand.x>=self.TankBounds[1]) and (self.control_inputs.u_U*cos(self.robotcommand.psi)>0)) or ((self.robotcommand.x<=self.TankBounds[0]) and (self.control_inputs.u_U*cos(self.robotcommand.psi)<0)))):
            self.robotcommand.x += dt*(self.control_inputs.u_U*cos(fishstate.psi))

            
        if(not (((self.robotcommand.y>=self.TankBounds[3]) and (self.control_inputs.u_U*sin(self.robotcommand.psi)>0)) or ((self.robotcommand.y<=self.TankBounds[2]) and (self.control_inputs.u_U*sin(self.robotcommand.psi)<0)))):
            self.robotcommand.y += dt*(self.control_inputs.u_U*sin(fishstate.psi))

        if(not (((self.robotcommand.z>=self.TankBounds[5]) and (self.control_inputs.u_z>0)) or ((self.robotcommand.z<=self.TankBounds[4]) and (self.control_inputs.u_z<0)))):
            self.robotcommand.z += dt*(self.control_inputs.u_z)
        if(brainstate == ("swim" or "huntswim" or "huntcapture" or "coast")):
            # self.robotcommand.tilt = atan2(uz,uplanar)
            self.robotcommand.tilt = 0 #atan2(self.robotcommand.zdot,self.robotcommand.U)
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
