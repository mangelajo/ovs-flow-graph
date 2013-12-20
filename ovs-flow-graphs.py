import ofctl

class OFCTLRulesToDOT:
    def __init__(self,rules):

        self.tables = {}

        for rule in rules:
            table_number = int(rule['data']['table'])
            if self.tables.has_key(table_number):
                self.tables[table_number].append(rule)
            else:
                self.tables[table_number] = [rule]

    def get_dot(self):
        return self.render()

    def render(self):
        self._dot = ""
        self.add_header()

        for table_nr,rules in self.tables.items():
            self.add_table(table_nr,rules)

        for table_nr,rules in self.tables.items():
            self.add_connections(table_nr,rules)

        self.add_footer()
        return self._dot

    def add_header(self):
        self.add("digraph G"
                 "{"
                 " rankdir = LR;")

    def add_table(self,table_nr,rules):
        self.add_table_header(table_nr)
        rule_id = 0
        for rule in rules:
            self.add_table_rule(rule,rule_id)
            rule_id += 1

        self.add_table_footer(table_nr)

    def add_table_header(self,table_nr):
        self.add(" table%d"%table_nr)
        self.add(" [")
        self.add("  shape = none")
        self.add('  label = <<table border="0" cellspacing="0">')
        self.add('   <tr><td port="header" border="1" colspan="5" '
                 'bgcolor="red">TABLE %d</td></tr>' % table_nr)
        self.add('   <tr>')
        self.add('    <td border="1">in</td>')
        self.add('    <td border="1">packets</td>')
        self.add('    <td border="1">bytes</td>')
        self.add('    <td border="1">idle</td>')
        self.add('    <td border="1">actions</td>')
        self.add('   </tr>')

    def add_table_rule(self,rule,rule_id):
        data = rule['data']
        actions = rule['actions']

        in_port = ""
        if data.has_key('in_port'):
            in_port +="port:%s" % data['in_port']
        if data.has_key('tun_id'):
            in_port +="tun:%s" % data['tun_id']

        action_str = ""
        for action in actions:

            if type(action)==str:
                action_str += action+","
            if type(action)==dict:
                action_str += action.keys()[0]+","

        self.add('   <tr>')
        self.add('    <td border="1">%s</td>' % in_port )
        self.add('    <td border="1">%s</td>' % data['n_packets'])
        self.add('    <td border="1">%s</td>' % data['n_bytes'])
        self.add('    <td border="1">%s</td>' % data['idle_age'])
        self.add('    <td port="rule%d" border="1"> %s </td>'% (rule_id,action_str))
        self.add('   </tr>')

    def add_table_footer(self,table_nr):
        self.add('    </table>>')
        self.add('  ]')


    def add_connections(self,table_nr,rules):
        rule_id = 0
        for rule in rules:
            self.add_table_connection(table_nr,rule,rule_id)
            rule_id += 1

    def add_table_connection(self,table_nr,rule,rule_id):
        #node1:port2 -> node2:port6 [label="language_id"]
        data = rule['data']
        actions = rule['actions']
        for action in actions:
            if type(action)==dict:
                for function,params in action.items():
                    if function=="resubmit":
                        self.add('table%d:rule%d -> table%s:header [label="resubmit"]' %(table_nr,rule_id,params))


    def add_footer(self):
        self.add("}\n")

    def add(self,content):
        self._dot += content +"\n"


class OFCTLDumpToDOT:
    def __init__(self,raw_tables):
        rules = ofctl.parse(raw_tables)
        self.rules_to_dot = OFCTLRulesToDOT(rules)

    def render(self):
        return self.rules_to_dot.render()



def main():
    with open("test-data/ovs-ofctl-dump-out.txt",'r') as file:

        ofctl_dot = OFCTLDumpToDOT(file.read())

        print ofctl_dot.render()


if __name__ == "__main__":
    main()