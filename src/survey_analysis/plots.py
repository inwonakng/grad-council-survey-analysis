from typing import Literal

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from pathlib import Path

def parse_json(col: pd.Series) -> pd.DataFrame:
    return pd.DataFrame([
        {v: True for v in json.loads(c.replace('\'','"'))}
        for c in col.fillna('[]').values
    ]).fillna(False)
    
def plot_population(
    df: pd.DataFrame,
    identifiers: dict[str,str],
    save_dir: str | Path | None = None,
):
    columns = []    
    if identifiers['grad_type']:
        columns += [identifiers['grad_type']]
    if identifiers['grad_year']:
        columns += [identifiers['grad_year']]
    if identifiers['is_undergrad']:
        columns += [identifiers['is_undergrad']]
    if identifiers['undergrad_year']:
        columns += [identifiers['undergrad_year']]
    
    fig, axes = plt.subplots(nrows =len(columns), figsize=(10, 4*len(columns)))

    if len(columns) > 1:
        for i, col in enumerate(columns):
            sns.barplot(
                orient='h',
                data = df[col].value_counts().reset_index(),
                y = col,
                x = 'count',
                ax = axes[i],
            ).set(
                title = col,
            )
    else:
        sns.barplot(
            orient='h',
            data = df[columns[0]].value_counts().reset_index(),
            y = columns[0],
        x = 'count',
        ax = axes,
    ).set(
        title = columns[0],
    )

    fig.suptitle(f'Population distribution')
    fig.tight_layout()
    if save_dir is not None:
        fig_file = Path(save_dir) / f'population.png'
        fig_file.parent.mkdir(exist_ok=True, parents=True)
        fig.savefig(
            fig_file,
            dpi = 300,
            bbox_inches = 'tight',
        )

def plot_2way_categorical_single(
    df: pd.DataFrame,
    target=str,
    by=str,
    save_dir: str | Path | None = None,
):
    valid_responses = df[~df[target].isna() & ~df[by].isna()]
    ncols = valid_responses[~valid_responses[by].isna()][by].unique().shape[0]
    fig, axes = plt.subplots(ncols = ncols+1, figsize = (4*ncols+4, 4), sharey = True)
    sns.barplot(
        data = valid_responses[target].value_counts().reset_index(),
        x = 'count',
        y = target,
        orient = 'h',
        ax = axes[0]
    ).set(
        title = f'Valid responses = {len(valid_responses)}'
    )
    for i, (idx, grouped) in enumerate(valid_responses.groupby(by)):
        sns.barplot(
            orient = 'h',
            data = grouped[target].value_counts().reset_index(),
            x = 'count',
            y = target,
            ax = axes[i+1],
        ).set(
            title = idx,
            xlabel = ''
        )
        
    fig.suptitle(f'"{target}" by "{by}"')
    fig.tight_layout()
    if save_dir is not None:
        fig_file = Path(save_dir) / f'{target}_by_{by}.png'
        fig_file.parent.mkdir(exist_ok=True, parents=True)
        fig.savefig(
            fig_file,
            dpi = 300,
            bbox_inches = 'tight',
        )

def plot_2way_categorical_multi(
    df: pd.DataFrame,
    target=str,
    by=str,
    save_dir: str | Path | None = None,
):
    parsed = parse_json(df[target])
    valid_by_vals = sorted(df[~df[by].isna()][by].unique())
    fig, axes = plt.subplots(ncols = len(valid_by_vals)+1, figsize = (4*len(valid_by_vals)+4, 4), sharey = True)

    sns.barplot(
        data = parsed.sum().reset_index(name='sum'),
        x = 'sum',
        y = 'index',
        orient = 'h',
        ax = axes[0],
    ).set(
        title = f'Valid responses = {(~df[by].isna()).sum()}'
    )

    for i, group in enumerate(valid_by_vals):
        sns.barplot(
            data = parsed[df[by]==group].sum().reset_index(name='sum'),
            x = 'sum',
            y = 'index',
            orient = 'h',
            ax = axes[i+1],
        ).set(
            title = group
        )
    fig.suptitle(f'"{target}" by "{by}"')
    fig.tight_layout()
    if save_dir is not None:
        fig_file = Path(save_dir) / f'{target}_by_{by}.png'
        fig_file.parent.mkdir(exist_ok=True, parents=True)
        fig.savefig(
            fig_file,
            dpi = 300,
            bbox_inches = 'tight',
        )
    
def plot_2way_categorical(
    df: pd.DataFrame,
    target:str,
    by:str,
    input_type: str,
    save_dir: str | Path | None = None,
):
    if input_type == 'multi-select':
        plot_2way_categorical_multi(
            df, 
            target=target, 
            by=by, 
            save_dir=save_dir
        )
    elif input_type == 'single-select':
        plot_2way_categorical_single(
            df, 
            target=target, 
            by=by,
            save_dir=save_dir
        )
    else:
        raise Exception('Unknown input type.')
    
def plot_2way_numeric(
    df: pd.DataFrame,
    target: str,
    by: str,
    kind: Literal['bar', 'line'] = 'bar',
    save_dir: str | Path | None = None,
):
    valid_by_vals = sorted(df[~df[by].isna()][by].unique())
    valid_responses = df[~df[target].isna() & ~df[by].isna()]

    if kind == 'line':
        plot_func = sns.kdeplot
    elif kind == 'bar': 
        plot_func = sns.histplot
    else:
        raise Exception('Unknown plot kind.')

    fig, axes = plt.subplots(ncols = len(valid_by_vals)+1, figsize = (4*len(valid_by_vals)+4, 4), sharey = True)
    plot_func(
        data = df[~df[target].isna()],
        x = target,
        ax = axes[0]
    ).set(
        xlabel = '',
        title = f'Valid responses = {len(valid_responses)}'
    )

    for i, group in enumerate(valid_by_vals):
        plot_func(
            data = valid_responses[valid_responses[by] == group],
            x = target,
            ax = axes[i+1]
        ).set(
            xlabel = '',
            title = group,
        )

    fig.suptitle(f'"{target}" by "{by}"')
    fig.tight_layout()
    if save_dir is not None:
        fig_file = Path(save_dir) / f'{target}_by_{by}.png'
        fig_file.parent.mkdir(exist_ok=True, parents=True)
        fig.savefig(
            fig_file,
            dpi = 300,
            bbox_inches = 'tight',
        )

def plot_response(
    df:pd.DataFrame,
    target: dict[str,str],
    by: str,
    numeric_plot_kind: Literal['bar','line'] = 'bar',
    save_dir: str | Path | None = None,
):
    if target['value_type'] == 'numeric':
       plot_2way_numeric(
           df, 
           target=target['question'], 
           by=by, 
           kind=numeric_plot_kind,
           save_dir=save_dir,
        )
    elif target['value_type'] == 'categorical':
        plot_2way_categorical(
            df, 
            target=target['question'],
            by=by,
            input_type=target['input_type'],
            save_dir=save_dir,
        )
    else:
        raise Exception('Unknown value type.')