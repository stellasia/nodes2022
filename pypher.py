# pip install python_cypher
from pypher import Pypher

q = Pypher()
q.Match.node('mark', labels='Person').WHERE.mark.property('name') == 'Mark'
q.RETURN.mark


assert str(q) == "MATCH (mark:`Person`) WHERE mark.`name` = NEO_9326c_1 RETURN mark"
assert q.bound_params == {'NEO_9326c_1': 'Mark'}
