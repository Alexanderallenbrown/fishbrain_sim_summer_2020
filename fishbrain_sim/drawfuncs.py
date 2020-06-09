import math 

def arrow(x1,y1,x2,y2): 
  line(x1, y1, x2, y2)
  pushMatrix()
  translate(x2, y2)
  a = atan2(x1-x2, y2-y1)
  rotate(a)
  line(0, 0, -10, -10)
  line(0, 0, 10, -10)
  popMatrix()

class TargetVizTop:
    def __init__(self,ox,oy,simscale,diam,pose,bounds):
        self.pose = pose
        self.ox = ox
        self.oy = oy
        self.simscale = simscale
        self.diam = diam
        self.bounds = bounds
    def drawTargetTop(self,contman):
        pushMatrix()
        translate(self.ox,self.oy)
        scale(self.simscale)
        strokeWeight(1.0/self.simscale)
        fill(color(255,0,0,0.15))
        stroke(0)
        ellipse(self.pose.x,self.bounds[3]-self.pose.y,self.diam,self.diam)
        #use the targeting controller class to get the radius
        shotdiam = 2*(self.pose.z-contman.tc.shotDepth)/math.tan(contman.tc.tiltAng)
        ellipse(self.pose.x,self.bounds[3]-self.pose.y,shotdiam,shotdiam)
        popMatrix()
        fill(255)
        

class TankVizTop:
    def __init__(self,ox,oy,simscale,bounds):
        self.ox = ox
        self.oy = oy
        self.simscale = simscale
        self.bounds = bounds
        self.fL = 0.1
    
    def drawTankTop(self):
        pushMatrix()
        translate(self.ox,self.oy)
        scale(self.simscale)
        strokeWeight(1.0/self.simscale)
        fill(255)
        stroke(0)
        rect(self.bounds[0],self.bounds[2],self.bounds[1]-self.bounds[0],self.bounds[3]-self.bounds[2])
        popMatrix()
    
    def drawFishTop(self,fishpose):
        pushMatrix()
        translate(self.ox,self.oy)
        scale(self.simscale)
        strokeWeight(1.0/self.simscale)
        translate(fishpose.x,self.bounds[3]-fishpose.y)
        ellipse(0,0,.01,.01)
        rotate(-fishpose.psi)
        line(0,0,self.fL/2,0)
        line(self.fL/2,0,0.8*self.fL/2,-.01)
        line(self.fL/2,0,0.8*self.fL/2,.01)
        popMatrix()
    
    def draw(self,fishpose):
        self.drawTankTop()
        self.drawFishTop(fishpose)
        

class TankVizFront:
    def __init__(self,ox,oy,simscale,bounds):
        self.ox = ox
        self.oy = oy
        self.simscale = simscale
        self.bounds = bounds
        self.fL = 0.1
    
    def drawTankFront(self):
        pushMatrix()
        translate(self.ox,self.oy)
        scale(self.simscale)
        strokeWeight(1.0/self.simscale)
        fill(255)
        stroke(0)
        rect(self.bounds[0],self.bounds[5],self.bounds[1]-self.bounds[0],self.bounds[5]-self.bounds[4])
        popMatrix()
    
    def drawFishFront(self,fishpose):
        pushMatrix()
        translate(self.ox,self.oy)
        scale(self.simscale)
        strokeWeight(1.0/self.simscale)
        translate(fishpose.x,self.bounds[5]-fishpose.z)
        ellipse(0,0,.01,.01)
        rotate(fishpose.tilt)
        line(0,0,self.fL/2*cos(fishpose.psi),0)
        line(self.fL/2*cos(fishpose.psi),0,0.8*self.fL/2*cos(fishpose.psi),-.01)
        line(self.fL/2*cos(fishpose.psi),0,0.8*self.fL/2*cos(fishpose.psi),.01)
        popMatrix()
    
    def draw(self,fishpose):
        self.drawTankFront()
        self.drawFishFront(fishpose)
        
        
        


class Button:
  def __init__(self,ix,iy,id,ilabel,itextSize,ilatching,ikeystring):
    self.x = ix;
    self.y = iy;
    self.d = id;
    self.state = False;
    self.touched = False;
    self.wastouched = False;
    self.newtouch = False;
    self.label = ilabel;
    self.textSize = itextSize;
    self.latching = ilatching;
    self.keystring = ikeystring;

  def updateButton(self):
    #detect whether the radio button is 
    if (mousePressed):
      if ((((mouseX-self.x)**2+(mouseY-self.y)**2)**.5<=self.d/2)):
        self.touched=True;
      else:
        self.touched=False;
    else:
        self.touched=False
    self.newtouch = self.touched and  not self.wastouched;
    if(self.latching):
      if(self.newtouch):
        #print("hello from newtouch latching")
        self.state=not self.state
    else:
        self.state = self.touched

    #update value of touched
    self.wastouched = self.touched
    #draw the button
    self.drawButton()
    
  def drawButton(self):
    if (self.state==False):
      fill(255);
    else:
      fill(0);
    
    stroke(0);
    strokeWeight(2);
    #draw the radio button
    ellipse(self.x, self.y, self.d, self.d);
    fill(0);
    stroke(0);
    textSize(self.textSize);
    textAlign(CENTER);
    text(self.label, self.x, self.y+1.1*self.d);
    strokeWeight(1);
