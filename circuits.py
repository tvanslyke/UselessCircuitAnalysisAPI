from sympy import *

s = symbols('s')

class Element(object):
    __totalElements = 0

    def __init__(self, val, nodes):
        self.value = float(val) if isinstance(val, int) else val
        self.impedance = self.value     # just make an intuitive name for it
        self.nodes = nodes
        self.solved = False
        Element.__totalElements += 1
        for node in self.nodes:
            node.connections.add(self)

    def getNode(self, requesting):
        return [node  for node in self.nodes if (node is not requesting)][0]
    
    def update(self):
        if self.nodes[0] and self.nodes[1] and not self.solved:
            self.voltage = self.nodes[0].voltage - self.nodes[1].voltage
            self.current = self.voltage / self.value
            self.solved = True
        return self.solved
    
    @staticmethod
    def count():
        return Element.__totalElements

class Resistor(Element):

    __count = 0
    def __init__(self, resistance, nodes):
        super(Resistor, self).__init__(resistance, nodes)
        self.current = None
        self.voltage = None
        self.solved = False
        Resistor.__count+=1

    def reset(self):
        self.solved = False
        
    @staticmethod
    def count():
        return Resistor.__count
    
class Capacitor(Element):

    __count = 0
    
    def __init__(self, capacitance, nodes):
        impedance = (capacitance * s)**-1
        super(Capacitor, self).__init__(impedance, nodes)
        self.current = None
        self.voltage = None
        self.solved = False
        Capacitor.__count+=1

    def reset(self):
        self.solved = False
        
        
    @staticmethod
    def count():
        return Capacitor.__count
    
class Inductor(Element):
    
    __count = 0
    
    def __init__(self, inductance, nodes):
        impedance = inductance * s
        super(Inductor, self).__init__(impedance, nodes)
        self.current = None
        self.voltage = None
        self.solved = False
        Inductor.__count+=1

    

    def reset(self):
        self.solved = False

    @staticmethod
    def count():
        return Inductor.__count




class Node(object):

    def __init__(self, voltage = None ):
        self.voltage = voltage
        self.connections = set()
        self.equation = None

    def assignVoltage(self, voltage):
        self.voltage = voltage
        
    def update(self):
        if self.voltage == None:    # should return True if self.voltage is zero
            return False
        equation = 0
        for element in self.connections:
            element.update()
        
        coeffs = {}
        rhs = 0
        if isinstance(self.voltage, Symbol):
            coeffs[self.voltage] = 0

        for element in self.connections:
            otherNode = element.getNode(self)
            thisTerm = otherNode.voltage
            if thisTerm == None:
                return False
            impedance = element.value
            if thisTerm is symbols('Vin') or not isinstance(thisTerm, Symbol):
                # if this term is Vin then subtract from right-hand side
                rhs -= thisTerm/impedance
            else:
                # if this term is symbolic but has not yet been encountered,
                # make a spot for it.  otherwise just add it
                if thisTerm in coeffs.keys() :
                    coeffs[thisTerm] += 1 / impedance
                else:
                    coeffs[thisTerm] = 1 / impedance
            
            if self.voltage is symbols('Vin') or not isinstance(self.voltage, Symbol):
                rhs += self.voltage/impedance
            else:
                if self.voltage in coeffs.keys():
                    coeffs[self.voltage] -= 1/impedance
                else:
                    coeffs[self.voltage] = -1 / impedance

        self.equation = coeffs, rhs
        print self.equation
        return True

class Circuit(object):


    
    def __init__(self):
        self.ground = Node(0)
        self.input = Node(symbols('Vin'))
        self.output = Node(symbols('Vout'))
        self.nodes = set([self.ground])
        self.Elements = set()
        self.equations = []


    def addElement(self, elementType = 'R', value = None, nodes = None):
        typeMap = {'R': Resistor, 'C': Capacitor, 'L': Inductor}
        className = typeMap[elementType]
        if not nodes:
            return False
        if not value:
            value = elementType + str(className.count() + 1)
        
        #try:
        newElement = className(symbols(value) if isinstance(value, str) else value, nodes)
        self.Elements.add(newElement)
        #except:
        #    return False
        self.nodes = set.union(self.nodes, set(nodes))
        return True

    def update(self):
        success = True
        for node in self.nodes:
            if not node.update():
                success = False
        return success



    def transfer(self):
        if not self.update():
            print 'Update Failed'
            return None
        
        allSyms = set()
        
        for node in self.nodes:
            if (node.equation not in self.equations) and\
            ((node is not self.ground) and (node is not self.input)):
                self.equations.append(node.equation)
                allSyms = set.union(allSyms, set(self.equations[-1][0].keys()))
        syms = list(allSyms)

        dims = (len(self.equations), len(syms))
        LHS = [[0]*dims[1] for _ in range(dims[0])]
        RHS = [[0]]*dims[0]
        for row, (lhs, rhs) in enumerate(self.equations):
            RHS[row] = rhs
            for var, coeff in [(key, lhs[key]) for key in lhs.keys()]:
                LHS[row][syms.index(var)] = coeff
                
        LHS = Matrix(LHS)
        RHS = Matrix(RHS)
        solns = (LHS**-1) * RHS

        Vout =solns[syms.index(Symbol('Vout'))]
        Vin_solve = solve(solns[syms.index(Symbol('Vout'))] - 1, Symbol('Vin'))[0]

        return 1/Vin_solve
            
    


if __name__ == '__main__':
    circ = Circuit()
    v1 = Node(symbols('V1'))
    circ.addElement('R', 50, [circ.input, v1])
    
    circ.addElement('L', 2*10**-3, [v1, circ.output])
    circ.addElement('C', 5* 10 ** -6, [circ.output, circ.ground])
    soln = circ.transfer()
    print pretty(simplify(soln))
    #print pretty(inverse_laplace_transform(soln, s, Symbol('t')))
    nodes = circ.nodes
    eqns = circ.equations
    
    #for node in nodes:
    #    print node.voltage,':\t',pretty(node.equation)









