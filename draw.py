#!/bin/python3
import csv
import os
from pkgutil import get_data
from tkinter import font
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
print(plt.rcParams["figure.figsize"])
plt.rcParams["figure.figsize"] = (6.4,2.3)

RESULTS_DIR = "results"
FIGURES_DIR = "figures"
DATASETS = ["dbpedia", "kadaster", "energie"]
DATASET_LABELS = ["DBpedia", "Kadaster", "RVO"]
DIFF_MODULOS = [10, 100, 1000]

NOT_APPLICABLE = '-'

COLORS = {
    'kadaster': 'blue',
    'energie': 'red',
    'dbpedia': 'green'
}

def lighten_color(color, amount=0.5):
    return color
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.

    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])

def read_csv(filename):
    headers = None
    resultRows = []
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if len(row)<1:continue
            if headers is None:
                headers = row
                continue
            obj = {}
            for i in range(len(headers)):
                value = row[i]
                key = headers[i]
                # print(key,value)
                if key == "samplesize" or key == "peakmem" or key == 'stage' or key == 'modulo' and value!='':
                    value = int(value)
                    if key=="peakmem":
                        value=float(value)/1024
                elif key == 'diffsize':
                    value = float(value)
                elif key == 'runtime':
                    parts = value.split(':')
                    seconds = float(parts.pop(-1))  # seconds.milliseconds
                    seconds += int(parts.pop(-1))*60  # minutes
                    if (len(parts) > 0):
                        seconds += int(parts.pop(-1))*60*60  # hours
                    value = seconds
                obj[key] = value
            resultRows.append(obj)

    if 'stage' in resultRows[0]:
        # collapse stages into one
        newdps = []
        bucket = []
        for dp in resultRows:
            # if we've filled up a bucket, aggregate its values and place it in newdps
            if len(bucket) > 0 and dp['stage'] == 1:
                newdp = bucket[0].copy()
                newdp['runtime'] = sum([i['runtime'] for i in bucket])
                newdp['peakmem'] = max([i['peakmem'] for i in bucket])
                newdps.append(newdp)
                bucket = []
            bucket.append(dp)
        newdp = bucket[0].copy()
        newdp['runtime'] = sum([i['runtime'] for i in bucket])
        # print(newdps)
        newdp['peakmem'] = max([i['peakmem'] for i in bucket])
        newdps.append(newdp)
        resultRows = newdps
    return resultRows


def draw_1(experiment_name):
    print('drawing ', experiment_name)
    data = read_csv(f'{RESULTS_DIR}/{experiment_name}.csv')
    for statistic in ['runtime', 'peakmem']:
        fig, ax = plt.subplots()
        ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax.get_yaxis().get_major_formatter().labelOnlyBase = False
        ax.spines['top'].set_visible(False)
        # ax.spines['right'].set_visible(False)
        # ax.spines['bottom'].set_visible(False)
        # ax.spines['left'].set_visible(False)
        ax.set_yscale('log')
        labels = DATASET_LABELS
        x = np.arange(len(labels))  # the label locations
        width = 0.35  # the width of the bars
        rects=[]
        colors=[lighten_color('#1f77b4'), lighten_color('#ff7f0e'),'#1f77b4', '#ff7f0e']

        subset=data
        static_vals = [[i[statistic] for i in subset if i['variant'] == 'static' and i['dataset']==dataset] for dataset in DATASETS]
        dynamic_vals = [[i[statistic] for i in subset if i['variant'] == 'dynamic' and i['dataset']==dataset] for dataset in DATASETS]
        static_means = [round(sum(i)/len(i),2) for i in static_vals]
        dynamic_means = [round(sum(i)/len(i),2) for i in dynamic_vals]
                    
        rects.append(ax.bar(x - width/2, static_means, width, label='Static' , color=colors.pop(0)))
        rects.append(ax.bar(x + width/2, dynamic_means, width, label='Dynamic', color=colors.pop(0)))

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel("Runtime (seconds)" if statistic ==
                      'runtime' else "Peak memory usage (RSS, MB)")
        # ax.set_title(f'{statistic} by dataset and variant')
        ax.set_xticks(x, labels)
        ax.legend(loc="upper right")
        for r in rects:
            ax.bar_label(r, padding=3)
            ax.bar_label(r, padding=3)

        fig.tight_layout()

        plt.savefig(f'{FIGURES_DIR}/{experiment_name}-{statistic}.png')
        plt.clf()

def draw_2346(experiment_name):
    print('drawing ', experiment_name)
    data = read_csv(f'{RESULTS_DIR}/{experiment_name}.csv')
    labels = DATASET_LABELS
    
    for statistic in ['runtime', 'peakmem']:
        
        static_vals = [[i[statistic] for i in data if i['variant'] == 'static' and i['dataset']==dataset]for dataset in DATASETS]
        dynamic_vals = [[i[statistic] for i in data if i['variant'] == 'dynamic' and i['dataset']==dataset]for dataset in DATASETS]
        static_means = [round(sum(i)/len(i),2) for i in static_vals]
        dynamic_means = [round(sum(i)/len(i),2) for i in dynamic_vals]

        x = np.arange(len(labels))  # the label locations
        width = 0.35  # the width of the bars

        fig, ax = plt.subplots()
        ax.get_yaxis().get_major_formatter().labelOnlyBase = False
        ax.spines['top'].set_visible(False)
        ax.set_yscale('log')
        rects1 = ax.bar(x - width/2, static_means, width, label='Static')
        rects2 = ax.bar(x + width/2, dynamic_means, width, label='Dynamic')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel("Runtime (seconds)" if statistic ==
                      'runtime' else "Peak memory usage (RSS, MB)")
        # ax.set_title(f'{statistic} by dataset and variant')
        ax.set_xticks(x, labels)
        ax.legend(loc="upper right")

        ax.bar_label(rects1, padding=3)
        ax.bar_label(rects2, padding=3)

        fig.tight_layout()

        plt.savefig(f'{FIGURES_DIR}/{experiment_name}-{statistic}.png')
        plt.clf()


def draw_5(experiment_name):
    print('drawing ', experiment_name)
    data = read_csv(f'{RESULTS_DIR}/{experiment_name}.csv')

    pairs = [['dbpedia', 'kadaster'], [
        'dbpedia', 'energie'], ['kadaster', 'energie']]

    pairs_labels = [['DBpedia', 'Kadaster'], [
        'DBpedia', 'RVO'], ['Kadaster', 'RVO']]
    labels = [f'{i[0]}+{i[1]}' for i in pairs_labels]

    for statistic in ['runtime', 'peakmem']:
        fig, ax = plt.subplots()
        ax.get_yaxis().get_major_formatter().labelOnlyBase = False
        ax.spines['top'].set_visible(False)
        ax.set_yscale('log')
        x = np.arange(len(labels))  # the label locations
        width = 0.35  # the width of the bars
        rects=[]
        colors=[lighten_color('#1f77b4'), lighten_color('#ff7f0e'),'#1f77b4', '#ff7f0e']
        subset=data
        static_vals = [[i[statistic] for i in subset if i['variant'] == 'static' and i['primary'] == pair[0] and i['secondary'] == pair[1]] for pair in pairs]
        dynamic_vals = [[i[statistic] for i in subset if i['variant'] == 'dynamic' and i['primary'] == pair[0] and i['secondary'] == pair[1]] for pair in pairs]
        static_means = [round(sum(i)/len(i),2) for i in static_vals]
        dynamic_means = [round(sum(i)/len(i),2) for i in dynamic_vals]

        rects.append(ax.bar(x - width/2, static_means, width, label='Static' , color=colors.pop(0)))
        rects.append(ax.bar(x + width/2, dynamic_means, width, label='Dynamic', color=colors.pop(0)))
        
        ax.set_ylabel("Runtime (seconds)" if statistic ==
                      'runtime' else "Peak memory usage (RSS, MB)")
        ax.set_xticks(x, labels)
        ax.legend(loc="upper right")
        for r in rects:
            ax.bar_label(r, padding=3)
            ax.bar_label(r, padding=3)

        fig.tight_layout()

        plt.savefig(f'{FIGURES_DIR}/{experiment_name}-{statistic}.png')
        plt.clf()

def draw_6(experiment_name):
    print('drawing ', experiment_name)
    data = read_csv(f'{RESULTS_DIR}/{experiment_name}.csv')

    labels = DATASET_LABELS

    for statistic in ['runtime', 'peakmem']:
        fig, ax = plt.subplots()
        ax.get_yaxis().get_major_formatter().labelOnlyBase = False
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_yscale('log')
        x = np.arange(len(labels))  # the label locations
        width = 0.35  # the width of the bars
        rects=[]
        colors=[lighten_color('#1f77b4'), lighten_color('#ff7f0e'),'#1f77b4', '#ff7f0e']


        subset =data
        static_vals = [[i[statistic] for i in subset if i['variant'] == 'static' and i['dataset']==dataset] for dataset in DATASETS]
        dynamic_vals = [[i[statistic] for i in subset if i['variant'] == 'dynamic' and i['dataset']==dataset] for dataset in DATASETS]
        static_means = [round(sum(i)/len(i),2) for i in static_vals]
        dynamic_means = [round(sum(i)/len(i),2) for i in dynamic_vals]
        
        rects.append(ax.bar(x - width/2, static_means, width, label='Static' , color=colors.pop(0)))
        rects.append(ax.bar(x + width/2, dynamic_means, width, label='Dynamic', color=colors.pop(0)))
        
        ax.set_ylabel("Runtime (seconds)" if statistic ==
                      'runtime' else "Peak memory usage (RSS, MB)")
        ax.set_xticks(x, labels)
        ax.legend(loc="upper right")
        for r in rects:
            ax.bar_label(r, padding=3)
            ax.bar_label(r, padding=3)

        fig.tight_layout()

        plt.savefig(f'{FIGURES_DIR}/{experiment_name}-{statistic}.png')
        plt.clf()

def draw_7(experiment_name):
    print('drawing ', experiment_name)
    data = read_csv(f'results/{experiment_name}.csv')
    labels = DATASET_LABELS
    base_colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    for statistic in ['runtime', 'peakmem']:
        colors=[lighten_color(i) for i in base_colors]+base_colors
        x = np.arange(len(labels)) 
        width = 0.23
        fig, ax = plt.subplots()
        ax.get_yaxis().get_major_formatter().labelOnlyBase = False
        ax.spines['top'].set_visible(False)
        ax.set_ylabel("Runtime (seconds)" if statistic == 'runtime' else "Peak memory usage (RSS, MB)")
        ax.set_xticks(x, labels)

        ax.set_yscale('log')
        fig.tight_layout()
        rects=[]
        bars = {
            'Static': {
                'filter_f': lambda i: i['variant'] == 'static' ,
                'means': []
            },
            '10%': {
                'filter_f': lambda i: i['variant'] == 'dynamic' and i['modulo'] == 10 ,
                'means': []
            },
            '1%': {
                'filter_f': lambda i: i['variant'] == 'dynamic' and i['modulo'] == 100,
                'means': []
            },
            '0.1%': {
                'filter_f': lambda i: i['variant'] == 'dynamic' and i['modulo'] == 1000,
                'means': []
            }
        }
        for dataset in DATASETS:
            subset = [i for i in data if i['dataset'] == dataset]
            for key in bars:
                values = [i[statistic]
                        for i in subset if bars[key]['filter_f'](i)]
                mean = sum(values)/len(values)
                bars[key]['means'].append(round(mean, 2))
        rects += [
            ax.bar(x-width*1.5, bars['Static']['means'], width, label='Static',color=colors.pop(0)),
            ax.bar(x-width*0.5, bars['10%']['means'], width, label='Dyn-10%',color=colors.pop(0)),
            ax.bar(x+width*0.5, bars['1%']['means'], width, label='Dyn-1%',color=colors.pop(0)),
            ax.bar(x+width*1.5, bars['0.1%']['means'], width, label='Dyn-0.1%',color=colors.pop(0))
        ]
        for i in rects:
            ax.bar_label(i, padding=2, fontsize=7)
        ax.legend(loc="upper right")
        plt.savefig(f'{FIGURES_DIR}/{experiment_name}-{statistic}.png')
        plt.clf()

draw_1('e1-rdf2hdt')
draw_2346('e2-hdt2rdf')
draw_2346('e3-term-prefix-search')
draw_2346('e4-triple-pattern-search')
draw_5('e5-hdt-union')
draw_6('e6-hdt-subtraction')
draw_7('e7-triple-updates')



def print_table(statistic):
    
    title=''
    if statistic=='runtime':
        title="Runtime, dynamic/static"
    else:
        title="Peak memory usage (RSS), dynamic/static"


    table=(f'''
\caption{{{title}}}
\\begin{{tabular}}{{ c | c | c | c}}
    Experiment & DBpedia & Kadaster & RVO \\\\
    \hline
''')
    for pair in [('e1-rdf2hdt','RDF-to-HDT'),('e2-hdt2rdf','HDT-to-RDF'),('e4-triple-pattern-search','Triple-search'),
        ('e3-term-prefix-search','Term-search'),('e6-hdt-subtraction','HDT subtraction'),('e7-triple-updates','RDF updates')
    ]:
        if pair[0]=='e4-triple-pattern-search':
            table+=('''
    \iftoggle{submission}{%
    }{
''')
        if pair[0]=='e6-hdt-subtraction':
            table+=('''
    }
''')
        data=[i for i in read_csv(f'results/{pair[0]}.csv')]
        values = []
        for dataset in DATASETS:
            if 'modulo' in data[0]:
                vals=[]
                for modulo in [10,100,1000]:
                    dyn=[i[statistic] for i in data if i['dataset']==dataset and i['variant']=='dynamic' and i['modulo']==modulo]
                    sta=[i[statistic] for i in data if i['dataset']==dataset and i['variant']=='static' and i['modulo']==modulo]
                    vals.append(str(round((sum(dyn)/len(dyn))/(sum(sta)/len(sta)),2)))
                values.append('/'.join(vals))
            else:
                dyn=[i[statistic] for i in data if i['dataset']==dataset and i['variant']=='dynamic']
                sta=[i[statistic] for i in data if i['dataset']==dataset and i['variant']=='static']
                values.append(str(round((sum(dyn)/len(dyn))/(sum(sta)/len(sta)),2)))
        table+=("    "+pair[1]+ " & "+ ' & '.join(values)+" \\\\\n")
    data=[i for i in read_csv(f'results/e5-hdt-union.csv')]
    values=[]
    for pair in [('dbpedia','kadaster'),('dbpedia','energie'),('kadaster','energie')]:
        dyn=[i[statistic] for i in data if i['primary']==pair[0] and i['secondary']==pair[1] and i['variant']=='dynamic']
        sta=[i[statistic] for i in data if i['primary']==pair[0] and i['secondary']==pair[1] and i['variant']=='static']
        values.append(str(round((sum(dyn)/len(dyn))/(sum(sta)/len(sta)),2)))
    hdtCat=' & '.join(values)+"\n"


    table+=(f'''    \hline 
    & DB.+Ka. &DB.+RVO & Ka.+RVO \\\\
    \hline
    HDT merging & {hdtCat}
\end{{tabular}}
''')
    return table

with open('summary-runtime.tex','w') as f:
    f.write(print_table('runtime'))

with open('summary-peakmem.tex','w') as f:
    f.write(print_table('peakmem'))
