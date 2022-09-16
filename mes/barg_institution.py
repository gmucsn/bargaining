from mTree.microeconomic_system.environment import Environment
from mTree.microeconomic_system.institution import Institution
from mTree.microeconomic_system.agent import Agent
from mTree.microeconomic_system.directive_decorators import *
from mTree.microeconomic_system.message import Message
import math
import random
import logging
import time
import datetime

@directive_enabled_class
class BargInstitution(Institution):
    """
    Barg Institution runs bargaining between buyer and seller.  It accepts
    bids and asks from agents and determines if they have a contract.

    Messages Received: 
    - init_institution, from Environment, payload = {'standing_bid': standing_bid, 
                                                    'standing_ask': standing_ask,}
    - start_bargaining, from Environment, payload = agent_addresses
    - end_bargaining, from Environment, payload = None
    - request_standing from agent, payload = None
    - bid, from Buyer Agent, payload = (bid, buyer_short_name)
    - ask, from Seller Agent, payload = (ask, seller_short_name)

    Messages Sent:
    - institution_confirm_init, to Environment, payload = None
    - contract, to Environment, payload = {'price': price, 
                                           'buyer_id': buyer_short_name,       
                                           'seller_id': seller_short_name,}
    """
    
    def prepare(self):
        self.agent_id = None
        self.offer_history = []
        self.standing_bid = int(self.get_property("starting_bid"))
        self.standing_bid_id = "INIT"
        self.standing_ask = int(self.get_property("starting_ask"))
        self.standing_ask_id = "INIT"
        self.barg_open = False
        self.num_agents = 2


    @directive_decorator("start_bargaining")
    def start_bargaining(self, message: Message):
        """
        Messages Handled :
        - start_period
            sender: Environment 
            payload:    Agent addresses 

        Messages Sent: 
         - start_round
            receiver: Agents 
            payload:   Institution address 
        """
        self.barg_open = True
        self.log_message(f">>>...>>>{self.address_book.get_addresses()}")
        self.log_message(f"...>>>...{self.address_book.get_agents()}")
        #self.shutdown_mes() #Used for testing
        
        for k in range(self.num_agents):
            agent = f"barg_agent.BargAgent {k+1}"
            self.log_message(f"<...> Institution [start_bargaining] agent = {agent}")
            self.send_message("bargaining_open", agent) 


    @directive_decorator("request_standing")
    def request_standing(self, message: Message):
        """
        Sends the standing bid or ask to agents.

        Messages Handled :
        - request_standing
            sender: Agent 
            payload:    None 

        Messages Sent: 
         - standing
            sender: Institution 
            payload: (self.standing_bid, self.standing_ask) 
        """
        agent_id = message.get_payload() #saves the agent short_name 
        self.log_message(f"...!!!...!!! standing {agent_id}")
        payload = (self.standing_bid, self.standing_ask)
        self.send_message("standing", agent_id, payload)
        #self.shutdown_mes() # Used for testing

    @directive_decorator("bid")
    def bid(self, message: Message):
        """
        Sends the standing bid or ask to agents.

        Messages Handled :
        - bid
            sender: Agent 
            payload: self.agent_bid 

        Messages Sent: 
         - 
            sender: Institution 
            payload:    None 
        """
        if self.barg_open == False: return
        self.agent_address = message.get_sender() #saves the agent address 
        payload = message.get_payload()
        self.agent_bid = payload['bid'] #saves the agent bid  
        self.agent_id = payload['short_name'] #saves the agent short_name
        self.log_data(f"id = {self.agent_id}, bid = {self.agent_bid}")

        if self.agent_bid >= self.standing_ask:
            self.barg_open = False
            contract = (self.agent_id, self.standing_ask_id, self.standing_ask)
            self.log_data(f"contract = {contract}")
            self.send_message("contract", "Environment", contract, True)
            #self.shutdown_mes() #Used for testing
 
        elif self.agent_bid < self.standing_ask:
            self.standing_bid = self.agent_bid
            self.standing_bid_id = self.agent_id

    @directive_decorator("ask")
    def ask(self, message: Message):
        """
        Sends the standing_ask to agents.
        Messages Handled :
        - ask
            sender: Agent 
            payload: self.agent_bid 

        Messages Sent: 
         - 
            sender: Institution 
            payload:    None 
        """
        if self.barg_open == False: return
        self.agent_address = message.get_sender() #saves the agent address 
        payload = message.get_payload()
        self.log_message(f"... <I> ... payload = {payload}")
        self.agent_ask = payload['ask'] #saves the agent bid  
        self.agent_id = payload['short_name'] #saves the agent short_name
        self.log_data(f"id = {self.agent_id}, ask = {self.agent_ask}")

        if self.agent_ask <= self.standing_bid:
            self.barg_open = False
            contract = (self.standing_bid_id, self.agent_id, self.standing_bid)
            self.log_data(f"contract = {contract}")
            self.send_message("contract", "Environment", contract, True)
            #self.shutdown_mes() #Used for testing

        elif self.agent_ask > self.standing_bid:
            self.standing_ask = self.agent_ask
            self.standing_ask_id = self.agent_id

    @directive_decorator("end_bargaining")
    def end_bargaining(self, message: Message):
        """
        Sends the end_round to agents.

        Messages Handled :
        - end_period
            sender: Environment 
            payload: None 

        Messages Sent: 
         - end_round
            sender: Agents 
            payload: None 
        """
        self.barg_open = False
