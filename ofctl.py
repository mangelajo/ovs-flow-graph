import re


class OFCTLDumpFlowParser:
    def __init__(self,data):
        self.data = data
        self.parse()

    def parse(self):

        rules = []

        lines = self._data_lines(self.data)
        for line in lines:
            line_fields = self._line_fields(line)
            if line_fields:
                rules.append(line_fields)

        return rules

    def _line_fields(self,line):

        parts = line.strip(' ').split("actions=")

        if len(parts)<2:
            return None

        keys_values = [field.strip(' ') for field in parts[0].split(",")]
        actions_parser = OFCTLActionsParser(parts[1])
        actions =  actions_parser.parse()

        conditions = {}
        for key_value in keys_values:
            key,value = key_value.split('=')
            conditions[key]=value

        return {'data':conditions,'actions':actions}


    def _data_lines(self,data):
        return data.split("\n")




class OFCTLActionsParser:
    def __init__(self,data):
        self.data = data

    def parse(self):
        actions = []
        while self.look_ahead():
            actions.append(self.get_action())
        return actions

    def get_action(self):

        # first we have a function name, or k from  k:v pair
        name = self.get_token_STR()

        # it was a k:v pair
        if self.look_ahead() == ':':
            self.get_char()
            value = self.get_token_STR()
            self.get_char()
            return {name:value}

        # it was a function call
        if self.look_ahead() == '(':
            self.get_char()
            parameters = self.get_token_PARAMS().strip(',')
            self.get_char()
            return {name:parameters}

        # it's a ',' or anything else... we clear it out
        self.get_char()
        return name


    def get_token_STR(self):

        name = ""
        while not self.look_ahead() in [':','(',',',None]:
            name += self.get_char()
        return name


    def get_token_PARAMS(self):
        name = ""
        while not self.look_ahead() in [')',None]:
            name += self.get_char()

        return name


    def get_char(self):
        if self.data_left():
            char = self.data[0]
            self.data = self.data[1:]
            return char
        else:
            return None

    def look_ahead(self):
        if self.data_left():
            return self.data[0]
        else:
            return None

    def data_left(self):
        return len(self.data)>0


def parse(data):
    parser = OFCTLDumpFlowParser(data)
    return parser.parse()

