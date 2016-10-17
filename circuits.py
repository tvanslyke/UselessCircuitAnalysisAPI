

class Element(object):


    def __init__(self, val, nodes):
        self.value = float(val)
        self.nodes = nodes
        for node in self.nodes:
            node.conections.append(self)

class Resistor(Element):
    
    def __init__(self, resistance, nodes):
        super(Resistor, self).__init__(resistance, nodes)
        self.current = None
        self.voltage = None
        self.solved = False

    def update(self):
        if self.nodes[0] and self.nodes[1] and not self.solved:
            self.voltage = self.nodes[0].voltage - self.nodes[1].voltage
            self.current = self.voltage / self.value
            self.solved = True
        return self.solved

    def reset(self):
        self.solved = False
    

    
        


class Node(object):

    def __init__(self, voltage = None ):
        self.voltage = voltage
        self.connections = []
        

