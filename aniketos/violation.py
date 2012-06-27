from collections import defaultdict

class Violations(dict):

    def __str__(self):
        retval = []
        for msgid, occurences in self.iteritems():
            retval.append("    %s" % msgid)
            for lineno, msg in occurences:
                retval.append("    | line %d\t\t%s" % (lineno, msg))

        return "\n".join(retval)
