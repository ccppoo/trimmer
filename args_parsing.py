import argparse
from dataclasses import dataclass
from utils import open_yaml

__all__ = [ "get_args" ]

ARGS_YAML_FILE = 'args.yaml'

def make_parser(argparser : argparse.ArgumentParser):

    yml = open_yaml(ARGS_YAML_FILE)

    for _, value in yml['options'].items():
        short_, long_ = value.pop('dest')
        type_ = eval(value['type'])
        default = value['default']
        help = value['help']
        argparser.add_argument(short_, long_, type=type_, default=default, help=help)

def get_args() -> argparse.Namespace:
    
    parser = argparse.ArgumentParser(description='Modifies a video file to play at different speeds when there is sound vs. silence.')
    make_parser(parser)
    args = parser.parse_args()
    
    return args