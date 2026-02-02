class tank():
    def __init__(self,screen=None,position=(200,100),angle=0,scale=0.1):
        self.position=position
        self.angle=angle
        self.scale=scale

    def update(self,screen,birdImage):