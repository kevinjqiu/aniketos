import ConfigParser
from aniketos.rule import Rule

class AniketosConfigParser(object):

    def _import(self, full_object_path):
        """Import the class specified in the path"""
        parts = full_object_path.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for s in parts[1:]:
            m = getattr(m, s)
        return m

    def _read_section(self, cp, section):
        return dict(cp.items(section))

    def _build_policies(self, cp, sections):
        retval = {}
        for section in sections:
            items = self._read_section(cp, section)
            _, name = section.split(':')
            type_ = items.pop('type')
            retval[name] = self._import(type_)(**items)
        return retval

    def _build_checkers(self, cp, sections, policies):
        retval = {}
        for section in sections:
            items = self._read_section(cp, section)
            _, name = section.split(':')
            type_ = items.pop('type')
            if 'policy' in items:
                items['policy'] = policies[items['policy']]
            retval[name] = self._import(type_)(**items)
        return retval

    def _build_rules(self, cp, sections, checkers):
        retval = {}
        for section in sections:
            items = self._read_section(cp, section)
            _, name = section.split(':')
            checker_names = map(str.strip, items.pop('checker').split(','))

            items['checkers'] = dict(
                [(checker_name, checkers[checker_name]) for checker_name in checker_names]
            )
            retval[name] = Rule(**items)
        return retval

    def readfp(self, fp):
        """Return a list of rules contained in the config file
        given by the file pointer."""
        cp = ConfigParser.ConfigParser()
        cp.readfp(fp)
        sections = cp.sections()

        # sort out policies, checkers and rules
        policy_sections = filter(lambda x:x.startswith('policy'), sections)
        checker_sections  = filter(lambda x:x.startswith('checker'), sections)
        rule_sections  = filter(lambda x:x.startswith('rule'), sections)

        policies = self._build_policies(cp, policy_sections)
        checkers = self._build_checkers(cp, checker_sections, policies)
        rules = self._build_rules(cp, rule_sections, checkers)

        return rules

