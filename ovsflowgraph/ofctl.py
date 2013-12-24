# -*- mode: python; coding: utf-8 -*-

__author__ = "Miguel Angel Ajo Pelayo"
__email__ = "miguelangel@ajo.es"
__copyright__ = "Copyright (C) 2013 Miguel Angel Ajo Pelayo"
__license__ = "GPLv3"


import subprocess


class OFCTLDumpFlowParser:
    def __init__(self,data):
        self.data = data
        self.parse()

    def parse(self):

        rules = []
        line_id = 0
        lines = self._data_lines(self.data)
        for line in lines:
            line_fields = self._line_fields(line)
            if line_fields:
                line_fields['id'] = line_id
                rules.append(line_fields)
                line_id += 1

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
        while self._look_ahead():
            actions.append(self._get_action())
        return actions

    def _get_action(self):

        # first we have a function name, or k from  k:v pair
        name = self._get_token_STR()

        # it was a k:v pair
        if self._look_ahead() == ':':
            self._get_char()
            value = self._get_token_STR()
            self._get_char()
            return {name:value}

        # it was a function call
        if self._look_ahead() == '(':
            self._get_char()
            parameters = self._get_token_PARAMS().strip(',')
            self._get_char()
            return {name:parameters}

        # it's a ',' or anything else... we clear it out
        self._get_char()
        return name


    def _get_token_STR(self):

        name = ""
        while not self._look_ahead() in [':','(',',',None]:
            name += self._get_char()
        return name


    def _get_token_PARAMS(self):
        name = ""
        while not self._look_ahead() in [')',None]:
            name += self._get_char()

        return name


    def _get_char(self):
        if self._data_left():
            char = self.data[0]
            self.data = self.data[1:]
            return char
        else:
            return None

    def _look_ahead(self):
        if self._data_left():
            return self.data[0]
        else:
            return None

    def _data_left(self):
        return len(self.data)>0


def parse(data):
    parser = OFCTLDumpFlowParser(data)
    return parser.parse()

def dump_bridge_flows(bridge):
    process = subprocess.Popen(['ovs-ofctl','dump-flows',bridge],
                               stdout = subprocess.PIPE,
                               stderr = subprocess.PIPE )

    out, err = process.communicate()

    return_code = process.wait()

    if return_code!=0:
        print "ERROR:",err
        return None

    return parse(out)
