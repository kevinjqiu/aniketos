CHECKER_TYPES = {}

def register_checker_type(name, clazz):
    global CHECKER_TYPES
    CHECKER_TYPES[name] = clazz

def get_checker_type(name):
    return CHECKER_TYPES[name]
