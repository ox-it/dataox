from humfrey.utils.resource import register

class Agent(object):
    email = property(lambda self:self.get_one_of('foaf:mbox', 'v:email'))

register(Agent, 'foaf:Agent', 'foaf:Person')
