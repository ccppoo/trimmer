import argparse
from dataclasses import dataclass
from utils import open_yaml
import sys
from codecs_config import current_pc_codec

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
    
    if 'codec' in sys.argv:
        codecs = current_pc_codec()
        
        print(f'ENCODE')
        for x in codecs.encodable.video_codecs.names:
            print(f'\t{x}')
        print()
        print(f'DECODE')
        for x in codecs.decodable.video_codecs.names:
            print(f'\t{x}')
        exit()

    parser = argparse.ArgumentParser(description='Modifies a video file to play at different speeds when there is sound vs. silence.')
    make_parser(parser)
    args = parser.parse_args()
    
    return args