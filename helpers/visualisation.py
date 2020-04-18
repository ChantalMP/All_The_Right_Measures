from matplotlib import pyplot as plt
from datetime import timedelta
from helpers.data_extractors import calculate_transmission_data, create_measure_success_tuple, extract_oxford_measure_data, generate_success_measure_dict
from random import choice
from collections import defaultdict
import numpy as np
import seaborn as sns

sns.set()


def get_measure_name(measure):
    measure_name, strictness = measure.split('_')
    strictness = int(strictness)
    if strictness == 1:
        measure_name = f'Low {measure_name}'
    elif strictness == 2:
        measure_name = f'Medium {measure_name}'
    elif strictness == 3:
        measure_name = f'High {measure_name}'
    return measure_name


def visualise_measures_for_country(country_dfs, country_name):
    daily_cases, dates = calculate_transmission_data(country_name, time_window=2)
    fig, ax = plt.subplots(figsize=(24, 10))
    ax.plot(daily_cases)
    colors = ['b', 'g', 'r', 'c', 'm', 'k']

    country_df = country_dfs[country_name]
    for idx, measure in enumerate(country_df.columns):
        if measure == 'Date' or country_df[measure].max() == 0:  # measure never taken
            continue

        try:
            measure_date = country_df['Date'][country_df[measure].idxmax()].date()
            adjusted_date = measure_date + timedelta(days=18)
            if adjusted_date not in dates:
                x_idx = 0
            else:
                x_idx = dates.index(adjusted_date)
            y_value = daily_cases[x_idx]
            if len(colors) == 0:
                colors = ['b', 'g', 'r', 'c', 'm', 'k']

            color = choice(colors)
            colors.remove(color)
            ax.axvline(x=x_idx, ymin=0, ymax=1, color=color, alpha=1.0)
            measure_name = get_measure_name(measure)
            ax.text(x_idx, idx * max(daily_cases) / 30, measure_name, color=color, fontsize=20)

        except Exception as e:
            pass


def visualise_measure_ranking(country_dfs):
    measure_dict = generate_success_measure_dict(country_dfs)

    measure_list = sorted(measure_dict.items(), key=lambda x: x[1])
    measures, effect = zip(*measure_list)
    effect = 1 / np.array(effect)
    measures = [get_measure_name(measure) for measure in measures]
    plt.figure(figsize=(30, 10))
    plt.xticks(rotation=-80, fontsize=20)
    plt.bar(x=measures, height=effect)


def visualise_effect_restriction_relation():
    plt.figure(figsize=(20, 20))
    img = plt.imread('generated_data/effect_restriction_diagram.png')
    plt.imshow(img)


if __name__ == '__main__':
    country_dfs = extract_oxford_measure_data()
    visualise_measures_for_country(country_dfs, "Germany")
