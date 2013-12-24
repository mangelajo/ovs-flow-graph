# -*- mode: python; coding: utf-8 -*-

__author__ = "Miguel Angel Ajo Pelayo"
__email__ = "miguelangel@ajo.es"
__copyright__ = "Copyright (C) 2013 Miguel Angel Ajo Pelayo"
__license__ = "GPLv3"


import subprocess

import jinja2

import ofctl
import test


DOT_TEMPLATE = """
digraph G
{
  rankdir=LR;
  {% for table in tables %}
  table{{ table.number }}
  [

      shape = none
      label = <<table border="0" cellspacing="0">
           <tr><td port="header" border="1" colspan="6"
                 bgcolor="red">TABLE {{ table.number }}</td>
           </tr>
           <tr>
              <td border="1">in</td>
              <td border="1">packets</td>
              <td border="1">bytes</td>
              <td border="1">idle</td>
              <td border="1">actions</td>
              <td border="1">outputs</td>
           </tr>

           {% for row in table.rows %}
           <tr>
              <td border="1">{{ row.in_port  }}</td>
              <td border="1">{{ row.n_packets }}</td>
              <td border="1">{{ row.n_bytes  }}</td>
              <td border="1">{{ row.idle_age }}</td>
              <td border="1">{{ row.actions  }}</td>
              <td port="rule{{ row.rule_id }}" border="1">{{ row.outputs }}</td>
           </tr>
           {% endfor %}
          </table>>
  ]
  {% endfor %}

  {% for connection in connections %}
        table{{ connection.src_table }}:rule{{ connection.src_rule }} ->
           table{{ connection.dst_table }}:header [{{connection.parameters}}]
  {% endfor %}

}
"""

class OFCTLRulesToDOT:

    def __init__(self,rules):

        self.template = jinja2.Template(DOT_TEMPLATE)
        self.tables = {}
        self._add_rules(rules)

    def render(self):

        template_data = self._build_template_data()
        return self.template.render(template_data)


    def _add_rules(self, rules):

        for rule in rules:
            table_number = int(rule['data']['table'])
            if self.tables.has_key(table_number):
                self.tables[table_number].append(rule)
            else:
                self.tables[table_number] = [rule]


    def _build_template_data(self):

        tables = []
        connections = []

        for table_nr,rules in self.tables.items():
            tables.append(self._build_table_data(table_nr,rules))

        for table_nr,rules in self.tables.items():
            connections +=  self._build_connections(table_nr,rules)

        return {'tables': tables,
                'connections':connections }

    def _build_table_data(self,table_nr,rules):

        rows = [ self._build_rule_data(rule) for rule in rules ]
        return { 'number':table_nr, 'rows': rows}

    def _build_rule_data(self,rule):

        data = {}
        data['in_port'] = self._build_in_port_from_rule(rule)
        data['outputs'] = self._build_outputs_from_rule(rule)
        data['actions'] = self._build_actions_from_rule(rule)
        data['n_packets'] = rule['data']['n_packets']
        data['n_bytes'] = rule['data']['n_bytes']
        data['idle_age'] = rule['data']['idle_age']
        data['rule_id'] = rule['id']

        return data


    def _build_actions_from_rule(self,rule):

        actions = []

        for action in rule['actions']:
            if type(action)==str:
                actions.append(action)
            if type(action)==dict:
                action_name = action.keys()[0]
                action_params = action[action_name]
                if not action_name in ['output','resubmit','learn']:
                    actions.append(action_name)

        return ", ".join(actions)


    def _build_outputs_from_rule(self,rule):

        outputs = []
        for action in rule['actions']:
            if type(action)==dict:
                action_name = action.keys()[0]
                action_params = action[action_name]
                if action_name == "output":
                    outputs.append(action_params)

        return ", ".join(outputs)


    def _build_in_port_from_rule(self,rule):

        data = rule['data']
        in_port = ""
        if data.has_key('in_port'):
            in_port +="port:%s " % data['in_port']
        if data.has_key('tun_id'):
            in_port +="tun:%s " % data['tun_id']
        if data.has_key('vlan_tci'):
            in_port +="vlan:%s " % data['vlan_tci']
        if data.has_key('dl_dst'):
            in_port +="dst:%s " % data['dl_dst']
        if data.has_key('dl_vlan'):
            in_port +="vlan:0x%x " % int(data['dl_vlan'])

        return in_port


    def _build_connections(self,table_nr,rules):

        connections = []
        for rule in rules:
            table_connections = self._build_table_connection(table_nr,rule)
            connections += table_connections

        return connections


    def _build_table_connection(self,table_nr,rule):

        connections = []

        for action in rule['actions']:
            if type(action)==dict:
                connection = {}
                connection['src_table']=table_nr
                connection['src_rule']=rule['id']

                for function,params in action.items():
                    if function=="resubmit":
                        connection['dst_table']=params
                        connection['parameters']='arrowType="vee"'
                        connections.append(connection)
                    if function=="learn":
                        params = params.split(',')
                        table_param = params[0].split('=')[1] # table=xx
                        connection['dst_table']=table_param
                        connection['parameters']='label="learn"'
                        connections.append(connection)
        return connections

class OFCTLDumpToDOT:
    def __init__(self,raw_tables):
        rules = ofctl.parse(raw_tables)
        self.rules_to_dot = OFCTLRulesToDOT(rules)

    def render(self):
        return self.rules_to_dot.render()


def dump_bridge_flows(bridge):


    if bridge=="test":
        file = open(test.TestCase.get_data_path("ovs-ofctl-dump-out.txt"),'r')
        rules = ofctl.parse(file.read())
        file.close()
    else:
        rules = ofctl.dump_bridge_flows(bridge)

    rules_to_dot_renderer = OFCTLRulesToDOT(rules)

    dot = rules_to_dot_renderer.render()

    process = subprocess.Popen(['dot','-Tsvg'],
                               stdout = subprocess.PIPE,
                               stderr = subprocess.PIPE,
                               stdin  = subprocess.PIPE)

    process.stdin.write(dot)
    out, err = process.communicate()
    process.stdin.close()

    return_code = process.wait()

    if return_code!=0:
        print "ERROR:",err
        return None

    return out


def main():
    with open("data/../data/ovs-ofctl-dump-out.txt",'r') as file:

        ofctl_dot = OFCTLDumpToDOT(file.read())

        print ofctl_dot.render()


if __name__ == "__main__":
    main()