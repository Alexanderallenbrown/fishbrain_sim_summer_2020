from HybridFishBrain import FishState

def sign(inp):
    if(inp==0):
        out=0
    else:
        out=abs(inp)/inp
    return out

class SimGantry:
    def __init__(self,taurect = 0.05,taurot = 0.05,state = FishState(),vxmax = 0.3,vymax=.15,vzmax=0.05,tiltmax=1.0,yawmax = 6.0):
        self.state = state
        self.oldtime = 0
        self.vxmax = vxmax
        self.vymax = vymax
        self.vzmax = vzmax
        self.tiltmax = tiltmax
        self.yawmax = yawmax
        self.taurect = taurect
        self.taurot = taurot

    def update(self,command,timenow):
        dt = timenow-self.oldtime
        self.oldtime = timenow
        vx = dt/self.taurect*(command.x-self.state.x)
        if(abs(vx)>self.vxmax):
            vx = sign(vx)*self.vxmax
        vy = dt/self.taurect*(command.y-self.state.y)
        if(abs(vy)>self.vymax):
            vy = sign(vy)*self.vymax
        vz = dt/self.taurect*(command.z-self.state.z)
        if(abs(vz)>self.vzmax):
            vz = sign(vz)*self.vzmax
        vtilt = dt/self.taurot*(command.tilt-self.state.tilt)
        if(abs(vtilt)>self.tiltmax):
            vtilt = sign(vtilt)*self.tiltmax
        vyaw = dt/self.taurot*(command.psi-self.state.psi)
        if(abs(vyaw)>self.yawmax):
            vyaw = sign(vyaw)*(self.yawmax)

        self.state.x+=dt*vx
        self.state.y+=dt*vy
        self.state.z+=dt*vz
        self.state.tilt+=dt*vtilt
        self.state.psi+=dt*vyaw
        return self.state

