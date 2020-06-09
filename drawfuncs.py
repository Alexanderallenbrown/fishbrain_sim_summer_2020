def arrow(x1,y1,x2,y2): 
  line(x1, y1, x2, y2)
  pushMatrix()
  translate(x2, y2)
  a = atan2(x1-x2, y2-y1)
  rotate(a)
  line(0, 0, -10, -10)
  line(0, 0, 10, -10)
  popMatrix()


class TankViz:
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
        
    