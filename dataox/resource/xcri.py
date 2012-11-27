class Course(object):
    types = ('xcri:course',)
    #template_name = 'doc/course'

    @classmethod
    def _describe_patterns(cls):
        return [
            """\
%(uri)s mlo:specifies %(presentation)s .
OPTIONAL { %(presentation)s prog:has_event %(session)s } .
OPTIONAL { %(presentation)s mlo:start|xcri:end|xcri:applyFrom|xcri:applyTo %(date)s } .
OPTIONAL { %(presentation)s xcri:venue %(venue)s } .""",
            "%(provider)s mlo:offers %(uri)s"
        ]

class Presentation(object):
    types = ('xcri:presentation',)
