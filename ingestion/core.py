import argparse
import sys

import pandas as pd
import yaml

from .sheet import Sheet, authorize_creds


def parse_config(config_file):
    with open(config_file) as stream:
        conf = yaml.safe_load(stream)
    return conf


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--creds-file', default='credentials.json')
    parser.add_argument('--config-file', default='config.yml')
    parser.add_argument('--output-file', default='output.json')

    return parser.parse_args(argv)


def transform_df_record_to_pre_json(record, schema_mapping):
    return dict([
        (key, record.get(value)) for key, value in
        schema_mapping.items()
    ])


def transform_df_to_pre_json(frame, schema_mapping):
    return [
        transform_df_record_to_pre_json(row, schema_mapping) for row in frame.to_dict('records')
    ]


def main(args):
    conf = parse_config(args.config_file)
    gc = authorize_creds(args.creds_file)
    sheet = Sheet(gc, conf['spreadsheet_key'])
    aggregate = pd.concat([
        sheet.get_worksheet_df(worksheet_spec['name'], 6,
                               {'__CATEGORY': worksheet_spec['category']})
        for worksheet_spec in conf['worksheets']
    ],
                          axis=0)

    transformed = transform_df_to_pre_json(aggregate, conf['schema_mapping'])
    __import__('pdb').set_trace()
    print(transformed)


if __name__ == "__main__":
    main(parse_args(sys.argv[1:]))