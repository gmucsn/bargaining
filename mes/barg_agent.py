from tkinter.filedialog import askdirectory
from mTree.microeconomic_system.environment import Environment
from mTree.microeconomic_system.institution import Institution
from mTree.microeconomic_system.agent import Agent
from mTree.microeconomic_system.directive_decorators import *
from mTree.microeconomic_system.message import Message
import importlib
import math
import random
import logging
import time
import datetime

#TODO: make a directive to accept request_standing reminder message
@directive_enabled_class
class BargAgent(Agent):
    """
    Barg Test Agent class for the Microeconomic System.
    The Basic Agent class establishes a message framework to interact 
    with other institutions and accepts different strategies that 
    can be programmed to engage in varying behavior. 
    
    For more details on messages sent and received,
    see method docstrings. 

    Messages Received: 
    - init_agents, sent by DAEnvironment
    - start_exchange, sent by 

    Messages Sent
    """ 
    def __init__(self):
        self.my_id = None      
        self.role = None  
        self.value = None
        self.cost = None
        self.institution_address = None
        self.environment_address = None
        self.agent_dict = None
        self.offer_wait_time = 4
        self.contract = None
        self.current_standing = None
        self.standing_ask = None
        self.standing_bid = None
        self.barg_open = False
        

    def send_message(self, directive, receiver, payload, use_env):
        """Sends message
           use_env = True has method use environment address """
        new_message = Message()
        new_message.set_sender(self.myAddress)
        new_message.set_directive(directive)
        new_message.set_payload(payload)
        if use_env:
            receiver = "Environment"
            receiver_address = self.environment_address
        else:
            receiver_address = self.institution_address
        self.log_message(
            f"...<A>.. Message {directive} .. {payload}") 
        self.send(receiver_address, new_message)


    @directive_decorator("init_agent")
    def init_agent(self, message: Message):
        """
        Recieves the class variables for the agents and passes
        the payload dictionary to setup_agent. This method also 
        sends back a confirmation to the environment. 

        Messages Handled :
        - init_agents
            sender: Environment 
            payload = {'id': int,
                       'role': 'Buyer'|'Seller',
                       'value': int, or
                       'cost': int}

        Messages Sent: 
        - agent_confirm_init  
            receiver: Environment, 
            payload:  None
        """
        self.environment_address = message.get_sender() 
        payload = message.get_payload()
        self.my_id = payload['id']
        self.role = payload['role']
        if self.role == 'Buyer':
            self.value = int(payload['value'])
        else:
            self.cost = int(payload['cost'])

        self.log_message(f'***<A>*** {self.role}: Initialized')
        self.log_message(f'***<A>*** {self.role}: value/cost {self.value, self.cost}')

        self.send_message("agent_confirm_init", "Environment", None, True)

    @directive_decorator("bargaining_open")
    def bargaining_open(self, message: Message):
        """
        Informs agents that trading has started. 

        Messages Handled :
        - start_round
            sender: Institution
            payload: None

        Messages Sent:
        - request_standing
            receiver: Institution
        """
        self.institution_address = message.get_sender()
        self.barg_open = True
        
        self.send_message("request_standing", "Institution", self.short_name, False)
        self.log_data(f"value: {self.value}, cost: {self.cost}")
    
    @directive_decorator("make_offer")
    def make_offer(self, message: Message):
        if self.barg_open:
            self.send_message("request_standing", "Institution", 
                               self.short_name, False)

    def wait_offer(self):
        """
        Reminds agents every self.offer_wait_time seconds to make an offer.
        make_offer calls contracts, which calls standing, which calls make_bid and make_ask.

        Messages Handled :
        - make_offer
            sender: Self
            payload: None
        """
        offer_reminder = Message()
        offer_reminder.set_sender(self.myAddress)
        offer_reminder.set_directive('make_offer')
        self.reminder(seconds_to_reminder = self.offer_wait_time, message= offer_reminder)


    @directive_decorator("standing")
    def standing(self, message: Message):
        """
        Informs agents of standing_bid and standing_ask 

        Messages Handled :
        - standing
            sender: Institution
            payload: (self.standing_bid, self.standing_ask)
        """
        self.log_message(f'Agent {self.role}: Entered standing\n' +
                        f' payload = {message.get_payload()}')  
        
        self.standing_bid, self.standing_ask  = message.get_payload()
        self.log_message(f'..<<>>.. {self.standing_bid} {self.standing_ask}')

        if self.role == "Buyer":
            self.make_bid()
        elif self.role == "Seller":
            self.make_ask()
        else:
            self.log_message(f'Error: agent_role = {self.role} is incorrect')


    def make_bid(self): 
        """
        Sends a bid to the institution. 

        Messages Sent: 
        - bid
            receiver: Institution, 
            payload:  bid, short_name
        """

        bid = random.randint(10, self.value)
        payload = {'bid': bid, 'short_name': self.short_name}
        self.log_message(f'Agent {self.role}: Made bid {bid}: Payload = {payload}')
        self.send_message("bid", "Institution", payload, False)
        self.wait_offer()

 
    def make_ask(self): 
        """
        Sends a trade request for bidding on a commodity to DAInstitution, who 
        executes the trade if the amounts are valid. 

        INPUT:  price (price that the seller expects to receive),
                value (value that the seller expects to receive)

        Messages Sent: 
        - ask
            receiver: Institution, 
            payload:  ask, short_name
        """
        ask = random.randint(self.cost, 990)
        payload = {'ask': ask, 'short_name': self.short_name}
        self.log_message(f'Agent {self.role}: Made ask {ask}: Payload = {payload}')
        self.send_message("ask", "Institution", payload, False)
        self.wait_offer()


    @directive_decorator("contracts")
    def contracts(self, message: Message):
        """
        Informs agents of contracts.

        Messages Handled :
        - standing
            sender: Environment
            payload: {"contract"}
        """
        pass

    
    @directive_decorator("end_round")
    def end_round(self, message: Message):
        """
        Informs agents the round has ended and no further offers can be made.

        Messages Handled :
        - standing
            sender: Insitution
            payload: None
        """
        pass
