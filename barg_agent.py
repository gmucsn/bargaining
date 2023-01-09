
@directive_enabled_class
class BargAgent(Agent):
    def prepare(self):
        ...
        if self.my_id == 1:        
            self.role = 'Buyer'
            self.value = int(self.get_property("value"))
        
    @directive_decorator("bargaining_open")
    def bargaining_open(self, message: Message):
        self.send_message("request_standing", "barg_institution.BargInstitution", self.short_name)
        
    @directive_decorator("make_offer")
    def make_offer(self, message: Message):
        if self.barg_open:
            self.send_message("request_standing", "barg_institution.BargInstitution", self.short_name)

    def wait_offer(self):
        offer_reminder = Message()
        offer_reminder.set_sender(self.myAddress)
        offer_reminder.set_directive('make_offer')
        self.reminder(seconds_to_reminder = self.offer_wait_time, message= offer_reminder)


    @directive_decorator("standing")
    def standing(self, message: Message):
        ...
        self.standing_bid, self.standing_ask  = message.get_payload()
        if self.role == "Buyer":
            self.make_bid()

    def make_bid(self): 
        bid = random.randint(10, self.value)
        payload = {'bid': bid, 'short_name': self.short_name}
        self.send_message("bid", "barg_institution.BargInstitution", payload)
        self.wait_offer()

    @directive_decorator("contracts")
    def contracts(self, message: Message):
        pass
    
    @directive_decorator("end_round")
    def end_round(self, message: Message):
        pass
