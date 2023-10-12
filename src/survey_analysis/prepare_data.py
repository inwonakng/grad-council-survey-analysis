import yaml
import json
import pandas as pd
import click

def is_list(col):
    for val in col:
        try: 
            json.loads(val.replace('\'','"'))
        except Exception:
            return False
    return True

def is_number(col):
    for val in col:
        try:
            float(val)
        except Exception:
            return False
    return True

def prepare_data(filename):
    df = pd.read_csv(filename)

    file_setting = {
        'identifiers': {
            'grad_type': '',
            'grad_year': '',
            'is_undergrad': '',
            'undergrad_year': '',
        },
        'useful_columns': [
        ],
    }

    useful_columns = []

    for c in df.columns:
        nonempty_rows = df[~df[c].isna()]
        if (
            (nonempty_rows[c].value_counts() > 1).any()
            and nonempty_rows[c].unique().shape[0] < nonempty_rows.shape[0] / 2
        ):
            if (
                'version' in c.lower() 
                or 'sample' in c.lower() 
                or 'unnamed' in c.lower()
            ): 
                continue

            is_multi = is_list(nonempty_rows[c])
            is_num = is_number(nonempty_rows[c])

            if not is_num: 
                valid_unique_values = [g.lower() for g in nonempty_rows[c].unique()]
                if 'phd' in valid_unique_values or 'ph.d.' in valid_unique_values:
                    print('Possible GRAD TYPE column')
                    print(c)
                    file_setting['identifiers']['grad_type'] = c
                    continue

                if 'senior' in valid_unique_values:
                    print('Possible UNDERGRAD TYPE column')
                    print(c)
                    file_setting['identifiers']['undergrad_year'] = c
                    continue

                if 'year' in c.lower() and not 'senior' in valid_unique_values:
                    print('Possible GRAD YEAR column')
                    print(c)
                    file_setting['identifiers']['grad_year'] = c
                    continue
            
            if is_num and 'year' in c.lower():
                print('Possible GRAD YEAR column')
                print(c)
                file_setting['identifiers']['grad_year'] = c
                continue

            if 'undergrad' in c.lower():
                print('Possible IS UNDERGRADE column')
                print(c)
                file_setting['identifiers']['is_undergrad'] = c
                continue
            
            input_type = 'single-select'
            if is_multi: 
                input_type = 'multi-select'
                
            value_type = 'categorical'
            if is_num:
                value_type = 'numeric'
                
            print('question:', c)
            print('input type:', input_type)
            print('value type:', value_type)

            useful_columns += [{
                # 'name': '',
                'question': c,
                'input_type': input_type,
                'value_type': value_type,
            }]

    file_setting['useful_columns'] = useful_columns
    # yaml.safe_dump(file_setting, open(filename.replace('.csv','-columns.yaml'),'w'))
    return file_setting

@click.command()
@click.argument('filename')
def run_prepare_data(filename):
    prepare_data(filename)

if __name__ == "__main__":
    run_prepare_data()