from matplotlib import pyplot as plt
from datetime import timedelta
from helpers.data_extractors import calculate_transmission_data, create_measure_success_tuple, extract_oxford_measure_data, generate_success_measure_dict, \
    forecast_for_country
from random import choice
from collections import defaultdict
import numpy as np
import seaborn as sns
import pandas as pd
import ipywidgets as widgets
from ipywidgets import interact, fixed, interact_manual

from IPython.display import display
from ipywidgets import Button, HBox, VBox, Layout

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


def visualize_country_forecast(country_dfs, country_name, active_measures_override=None):
    plt.figure(figsize=(20, 10))
    x_axis, daily_cases, weekly_x_axis, weekly_new_cases = forecast_for_country(country_dfs, country_name, active_measures_override=None)
    plt.plot(x_axis, daily_cases, 'b')
    plt.plot(weekly_x_axis, weekly_new_cases, 'k')

    if active_measures_override is not None:
        _, _, weekly_x_axis, weekly_new_cases = forecast_for_country(country_dfs, country_name, active_measures_override=active_measures_override)
        plt.plot(weekly_x_axis, weekly_new_cases, 'r')

    plt.show()


def create_toggle_buttons(country_dfs, country_name):
    country_df = country_dfs[country_name]
    date = pd.Timestamp('2020-04-15')

    current_measures_in_country = country_df.loc[country_df['Date'] == date]
    active_measures = []
    toggle_buttons = []

    for measure, active in current_measures_in_country.iteritems():
        if measure != "Date" and active.tolist()[0] == 1:
            active_measures.append(measure)

    for measure in sorted(country_df.columns):
        if measure == 'Date' or measure == 'Travel Restrictions_3' or measure == 'Awareness Campaigns_2' or measure == 'Awareness Campaigns_3' or measure == 'Contact Tracing_3':  # exclude measures that were never performed
            continue

        value = measure in active_measures

        toggle_button = widgets.ToggleButton(
            value=value,
            description=measure,
            layout=Layout(width='25%', height='40px'),
            disabled=False,
            button_style='',  # 'success', 'info', 'warning', 'danger' or ''
            icon='check'
        )

        toggle_buttons.append(toggle_button)

    for i in range(0, len(toggle_buttons), 4):
        h_box = HBox(toggle_buttons[i:i + 4])
        display(h_box)

    return toggle_buttons


'''

widgets.Button(
        description='Calculate',
        disabled=False,
        button_style='success',  # 'success', 'info', 'warning', 'danger' or ''
        icon='check'
    
    
    '''
if __name__ == '__main__':
    country_dfs = extract_oxford_measure_data()
    from ipywidgets import ToggleButton

    visualise_measures_for_country(country_dfs, "Germany")
