__all__ = [ "validate_options" ]

import yaml
import pprint


'''
(1) yaml 유효성 검사

'''

def validate_options() -> bool:
    pass

with open('helps.yaml', mode='r') as fp:
    f = yaml.safe_load(fp)
    print(f['options']['input']['names'])

    pprint.pprint(f)
