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
    Buyer or Seller agent in bargaining game
    """ 
    def prepare(self):
        self.my_id = int(self.short_name[-1])
        self.log_message(f'****<A> myid = {self.my_id}')
        if self.my_id == 1:        
            self.role = 'Buyer'
            self.value = int(self.get_property("value"))
        else:
            self.role = 'Seller'
            self.cost = int(self.get_property("cost"))

        self.offer_wait_time = 4
        self.barg_open = False

        self.log_message(f'***<A>*** {self.role}: Initialized')
        #self.log_message(f'***<A>*** {self.role}: value/cost {self.value, self.cost}')


    @directive_decorator("bargaining_open")
    def bargaining_open(self, message: Message):
        """
        Informs agents that bargaining has started. 
        """
        self.barg_open = True       
        self.send_message("request_standing", "barg_institution", self.short_name)
        #self.log_data(f"value: {self.value}, cost: {self.cost}")
    

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
        self.send_message("bid", "barg_institution", payload)
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
        self.send_message("ask", "barg_institution", payload)
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
            sender: Institution
            payload: None
        """
        pass
