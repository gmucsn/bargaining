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
class BargEnvironment(Environment):
    """
    The Bargain environment initializes the agents and the institutions using
    control variables in the config file.  The environment is responsible
    for sending the init messages to the agents and institution, and openming
    and closing the exchange.                  


    Messages Received:
    - start_environment, sent by mTree_runner
    - env_end_period, sent by self
    - agent_confirm_init, sent by BasicAgents
    - institution_confirm_init, sent by DAInstitution
    - contract, sent by DAInstitution


    Messages Sent
    - init_institution, payload = dict, keys: 'starting_bid', 'starting_ask'
    - init_agents, payload = dict, keys: 'id', 'role', 'value'|'cost'
    - start_bargaining, payload = None
    - end_bargaining, payload = None
    - contract, payload = contract, keys: 'buyer_id', 'seller_id', 'price'



    """

    def __init__(self):
        self.state = {}
        self.num_agents_responded = None

    def send_message(self, directive, receiver, payload):
        """Sends message"""
        new_message = Message()
        new_message.set_sender(self.myAddress)
        new_message.set_directive(directive)
        new_message.set_payload(payload)
        self.log_message(
            f"Message {directive} from Environment sent to {receiver}")
        receiver_address = self.address_book.select_addresses(
            {"short_name": receiver})
        self.send(receiver_address, new_message)

    def set_reminder(self, directive, seconds_to_reminder):
        """Sets a reminder to send a message"""
        reminder_msg = Message()
        reminder_msg.set_sender(self.myAddress)
        reminder_msg.set_directive(directive)
        self.reminder(seconds_to_reminder = seconds_to_reminder,
                      message = reminder_msg)

    def load_environment_state(self):
        """Loads the environment state from the config file"""

        # agent related
        self.state['endowment'] = int(self.get_property("endowment"))
        self.state['value'] = int(self.get_property("value"))
        self.state['cost'] = int(self.get_property("cost"))
       
        # Institution related
        self.state['starting_bid'] = int(self.get_property("starting_bid"))
        self.state['starting_ask'] = int(self.get_property("starting_ask"))

        # Environment related
        self.state['period_length'] = int(self.get_property("period_length"))
        self.state['number_of_agents'] = int(self.get_property("number_of_agents"))
        self.state['contract'] = None
   

    @directive_decorator("start_environment")
    def start_environment(self, message: Message):
        """
        This method starts the environment (automatically through mTree_runner)
        and initializes agents with basic information about their values or costs. 

        Messages Handled :
        - start_environment
            sender: None 

        """
        self.load_environment_state()

        """
        # Agent related
        self.state['endowment'] = int(self.get_property("endowment"))
        self.state['value'] = int(self.get_property("value"))
        self.state['cost'] = int(self.get_property("cost"))
       
        # Institution related
        self.state['starting_bid'] = int(self.get_property("starting_bid"))
        self.state['starting_ask'] = int(self.get_property("starting_ask"))

        # Environment related
        self.state['period_length'] = int(self.get_property("period_length"))
        self.state['number_of_agents'] = int(self.get_property("number_of_agents"))
        self.state['contract'] = None
        """

        self.set_reminder("env_end_period", self.state['period_length'])

        institution_payload = {'starting_bid': self.state['starting_bid'],
                               'starting_ask': self.state['starting_ask']}

        self.send_message("init_institution", 
                          "barg_institution.BargInstitution 1",
                           institution_payload)


    @directive_decorator("institution_confirm_init")
    def institution_confirm_init(self, message: Message):
        """
        Receives confirmation from the institution that its finished initializing. 
        """

        # Initialize counter
        self.num_agents_responded = 0

        # send agent roles and value/cost information
        agent_payload = {"id": 1, "role": "Buyer", 
                         "value": self.state['value'],}
        self.send_message("init_agent", "barg_agent.BargAgent 1",
                           agent_payload)
        agent_payload = {"id": 2, "role": "Seller", 
                         "cost": self.state['cost'],}
        self.send_message("init_agent", "barg_agent.BargAgent 2",
                           agent_payload)

 
    @directive_decorator("agent_confirm_init")
    def agent_confirm_init(self, message: Message):
        """
        Receives confirmation from the agents that they are finished initializing. 
        """
        self.num_agents_responded += 1
        if self.num_agents_responded == self.state['number_of_agents']:
            self.log_message(f"agents confirmed")
            payload = self.address_book.get_agents()
            self.send_message("start_bargaining", 
                              "barg_institution.BargInstitution 1",
                               payload)


    @directive_decorator("contract")
    def contract(self, message: Message):
        """
        Receives contract tuple from Institution.
        payload: (buyer, seller, price)
        """
        self.state['contract'] = message.get_payload()
        self.log_message(f"... <E> ... Contract received: {self.state['contract']}")
        self.send_message("end_bargaining", 
                        "barg_institution.BargInstitution 1",
                         None)

        self.set_reminder("shutdown", 5)

        #self.shutdown_mes() #Used for testing

    @directive_decorator("env_end_period")
    def env_end_period(self, message: Message):
        """
        Receives reminder to end_period. Sends end_bargaining to Institution
        """
        self.log_message(".... <E> ... Ending Bargaining")
        self.log_data("no contract")
        self.send_message("end_bargaining", 
                        "barg_institution.BargInstitution 1",
                         None)

        self.set_reminder("shutdown", 5)

    @directive_decorator("shutdown")
    def shutdown(self, message: Message):
        """
        shutdown system
        """
        self.shutdown_mes()
