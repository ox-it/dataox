class Agent(object):
    email = property(lambda self:self.get_one_of('foaf:mbox', 'v:email'))
