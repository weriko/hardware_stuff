9
        GPIO.output(pins[i],False)
def show_msg(msg,pins,show_time=2, entry= 26, final=22, on_time=4, between_time= 0.5, entry_char = "1010", final_char = "101"):

    for i in pins:
        GPIO.output(i,False)
    msg = parse_msg(msg)
    msg = [entry_char] + msg + [final_char]

    for m in msg:
        if m == "1010":
            GPIO.output(entry,True)
        elif m=="101":
            GPIO.output(final,True)
            time.sleep(on_time)
            GPIO.output(entry,False)
            GPIO.output(final,False)
        else:
            show_led(m,pins,show_time=show_time)
            time.sleep(between_time)
    is_running=False
    
    
from __future__ import print_function
import json
from twisted.internet import reactor, protocol
import pickle
from requests import get

class NodeAsServer(protocol.Protocol):
    
    def connectionMade(self):
        print("Started")
    def dataReceived(self, data):
        print("Data received...")
        try:
            print(data)
            data = json.loads(data)
        
        except:
            self.transport.loseConnection()#Maybe dont handle this?
        action=None
        try:
            action = data["action"]
            received_from_node = data["received_from_node"]
        except Exception as e:
            print(e)
            
            #self.transport.write(json.dumps(data).encode("ascii"))
            
            self.transport.write(b"Protocol error")
    
                
        elif action=="leds":

            pins = [19,13,6,5,0,11,9,10]
            entry = 26
            final = 22
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(entry,GPIO.OUT)
            GPIO.setup(final,GPIO.OUT)
            for i in pins:
                GPIO.setup(i,GPIO.OUT)
            msg = data.get("msg","None")
            if !is_running:
                is_running=True
                Process(target=lambda:show_msg(msg,pins,entry=entry,final=final,show_time=1)).start()
    
        
class NodeServerFactory(protocol.ServerFactory): #Used when node is acting as a server, receiving information from other nodes to verify, or from others to, for example, add a node to the network
    protocol = NodeAsServer
    def __init__(self,queue=None, node = None):
        if not queue:
            self.queue = []
        else:
            self.queue = queue
        if not node:
            self.node = Node()
        else:
            self.node = node
            
            
    def clientConnectionFailed(self, connector, reason):
        print("Connection failed - goodbye!")
       
    
    def clientConnectionLost(self, connector, reason):
        print("Connection lost - goodbye!")

class NodeHandler(protocol.Protocol): #Used when node sends data to other nodes
    
    
    def connectionMade(self):
        try:
            self.transport.write(self.factory.data.encode())
        except:
            self.transport.write(self.factory.data)
    
    def dataReceived(self, data):
     
        print("Server said:", data)
        self.transport.loseConnection()
    
    def connectionLost(self, reason):
        print("connection lost")

class EchoFactory(protocol.ClientFactory):
    protocol = NodeHandler
    
    def __init__(self,data=None,ip=None,port=None):
        self.data = data or "None"
        

    def clientConnectionFailed(self, connector, reason):
        print("Connection failed with node",reason)
       
    
    def clientConnectionLost(self, connector, reason):
        print("Connection closed with node")
       
class Node:
    def __init__(self,node_list =None, port = 9000, pub_ip =None):
        if not node_list:
            self.node_list = []
        else:
            self.node_list = node_list
        self.port = port
        if not pub_ip:
            pub_ip = get("https://api.ipify.org").text
        self.pub_ip=pub_ip 
        
    def start_as_server(self):
        self.factory = NodeServerFactory(node=self)
        
        reactor.listenTCP(self.port,self.factory)
       
        reactor.run()
    
    def add_node(self,node):
        self.node_list.append(node)
        
        
        
    def transmit_data(self,data):
        print(self.node_list)
        for n in self.node_list:
            try:
                if self.pub_ip!=n[0] or self.port!=n[1]:
                
                    f = EchoFactory(data = data,ip=n[0],port=n[1])
                    reactor.connectTCP(n[0], n[1], f)
                   
            except:
                pass
                
                
    
    
    def start(self):
     
        self.start_as_server()
        
            
            


def main():
    with open("nodes.json","r") as nd:
        j = json.load(nd)["data"]
        print(j)
        node = Node(node_list=j, port = 9000, pub_ip = None)
        
        print("Starting...")
        node.start()
    GPIO.cleanup()
    
    

if __name__ == '__main__':
    main()
    
