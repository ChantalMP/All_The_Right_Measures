import re
import json
from pathlib import Path
import csv

import requests
import pandas as pd

pd.options.mode.chained_assignment = None

from helpers.mappers import worldometer_country_name_mapper, acaps_measure_mapper, acaps_country_name_mapper, oxford_country_name_mapper, \
    who_country_name_mapper
from helpers.utils import generate_dates, generate_past_dates


def extract_oxford_measure_data():
    oxford_df = pd.read_csv('data/oxford_covid19_measures_dataset.csv',
                            usecols=['CountryName', 'Date', 'S1_School closing', 'S2_Workplace closing', 'S3_Cancel public events',
                                     'S4_Close public transport', 'S5_Public information campaigns', 'S6_Restrictions on internal movement',
                                     'S7_International travel controls', 'S12_Testing framework', 'S13_Contact tracing'])

    oxford_df.rename(columns={'CountryName': 'COUNTRY', 'S1_School closing': 'School Closure', 'S2_Workplace closing': 'Workplace Closure',
                              'S3_Cancel public events': 'Public Services Closure'
        , 'S4_Close public transport': 'Public Transport Closure', 'S5_Public information campaigns': 'Awareness Campaigns',
                              'S6_Restrictions on internal movement': 'Movement Restrictions', 'S7_International travel controls': 'Travel Restrictions',
                              'S12_Testing framework': 'Testing', 'S13_Contact tracing': 'Contact Tracing'}, inplace=True)

    oxford_df.dropna(subset=['Date'], inplace=True)
    oxford_df['Date'] = pd.to_datetime(oxford_df['Date'], format='%Y%m%d')

    oxford_df.fillna(0, inplace=True)
    with open('data/countries.txt') as f:
        countries = f.read().splitlines()

    dates = generate_dates()

    oxford_country_dfs = {}

    for country in countries:
        country_df = pd.DataFrame(
            columns=['Date', 'Public Gathering Limitations', 'School Closure', 'Public Services Closure', 'Border Closure', 'Partial Lockdown', 'Full Lockdown',
                     'Protective Gear', 'Flight Restrictions', 'Awareness Campaigns', 'Quarantine', 'Workplace Closure', 'Public Transport Closure',
                     'Movement Restrictions', 'Travel Restrictions', 'Testing', 'Contact Tracing'])

        country_df['Date'] = dates
        country_df['Date'] = pd.to_datetime(country_df['Date'])
        country_df.fillna(0, inplace=True)
        date_as_index = pd.Index(country_df['Date'])

        country_rows: pd.DataFrame = oxford_df.loc[oxford_df['COUNTRY'] == oxford_country_name_mapper(country)]
        country_rows.reset_index(drop=True, inplace=True)

        if len(country_rows) <= 0:
            print(country)
            print(oxford_country_name_mapper(country))
            raise Exception('False Country')

        for measure in country_rows.columns:
            if measure == 'COUNTRY' or measure == 'Date':
                continue

            if len(country_rows[measure].to_numpy().nonzero()[0]) > 0:
                measure_date = country_rows['Date'][country_rows[measure].to_numpy().nonzero()[0][0]]
                date_row_idx = date_as_index.get_loc(measure_date)
                country_df[measure][date_row_idx:] = 1  # Set all values corresponding to that measure to 1 beginning from that date

        oxford_country_dfs[country] = country_df

    return oxford_country_dfs


'''
Schools Closure
    Public Service Closure
    Partial Lockdown
    Full Lockdown
    Protective Gear
    Travel Restrictions (inclusive border)
    Flight Restrictions
    Awareness campaigns'''


def extract_acaps_measure_data():
    acaps_df = pd.read_excel('data/acaps_covid19_measures_dataset.xlsx', sheet_name=1, index_col=0,
                             usecols=['ID', 'COUNTRY', 'REGION', 'LOG_TYPE', 'CATEGORY', 'MEASURE', 'TARGETED_POP_GROUP', 'COMMENTS', 'DATE_IMPLEMENTED',
                                      'LINK'])

    acaps_df.dropna(subset=['DATE_IMPLEMENTED'], inplace=True)
    # df.dropna()
    # df['DATE_IMPLEMENTED'] = pd.to_datetime(df['DATE_IMPLEMENTED'])
    #
    # # non_complicance?
    # germany_rows = df.loc[df['COUNTRY'] == 'Germany']
    #
    # sorted_germany_rows = germany_rows.sort_values('DATE_IMPLEMENTED')

    # measures_to_consider = ['Limit public gatherings', 'Introduction of isolation and quarantine policies', 'International flights suspension',
    #                       'Border closure', 'Public services closure', 'Schools closure', 'Awareness campaigns']
    # Strengthening the public health system,Visa restrictions,General recommendations, Health screenings in airports and border crossings,Domestic travel restrictions,Curfews,Partial lockdown,Surveillance and monitoring
    # Testing policy,Full lockdown,Requirement to wear protective gear in public,strengthening the public health system,testing policy,Complete border closure

    # Testing policy should be integrated differently
    '''
    Schools Closure
    Public Service Closure
    Partial Lockdown
    Full Lockdown
    Protective Gear
    Travel Restrictions (inclusive border)
    Flight Restrictions
    Awareness campaigns
    '''
    with open('data/countries.txt') as f:
        countries = f.read().splitlines()

    dates = generate_dates()

    acaps_country_dfs = {}

    for country in countries:
        country_df = pd.DataFrame(
            columns=['Date', 'Public Gathering Limitations', 'School Closure', 'Public Services Closure', 'Border Closure', 'Partial Lockdown', 'Full Lockdown',
                     'Protective Gear', 'Flight Restrictions', 'Awareness Campaigns', 'Quarantine'])

        country_df['Date'] = dates
        country_df['Date'] = pd.to_datetime(country_df['Date'])
        country_df.fillna(0, inplace=True)
        date_as_index = pd.Index(country_df['Date'])

        country_rows: pd.DataFrame = acaps_df.loc[acaps_df['COUNTRY'] == acaps_country_name_mapper(country)]
        for idx, country_row in country_rows.iterrows():
            measure = acaps_measure_mapper(country_row['MEASURE'].lower().strip())
            if measure:
                date_row_idx = date_as_index.get_loc(country_row['DATE_IMPLEMENTED'])
                country_df[measure][date_row_idx:] = 1  # Set all values corresponding to that measure to 1 beginning from that date

        acaps_country_dfs[country] = country_df

    return acaps_country_dfs


def extract_case_numbers(country_name, use_who_data=True):
    if use_who_data:
        who_data_path = Path('generated_data/cases/who_new_cases.csv')
        if not who_data_path.exists():
            who_data_url = 'https://covid.ourworldindata.org/data/ecdc/new_cases.csv'
            r = requests.get(who_data_url)
            with who_data_path.open('wb') as f:
                f.write(r.content)

        who_df = pd.read_csv(who_data_path)
        country_rows = who_df[who_country_name_mapper(country_name)].dropna()
        daily_new_cases_data = country_rows.tolist()
        active_cases_data = []

    else:

        key = worldometer_country_name_mapper(country_name)
        url = f"https://www.worldometers.info/coronavirus/country/{key}/"
        r = requests.get(url)
        as_str = r.content.decode()

        daily_new_cases_data = re.findall(r"Daily New Cases'.*? yAxis:.*?data:.*?\[([\d|null,]*)\]?", as_str, re.DOTALL)[0].split(',')
        active_cases_data = re.findall(r"Active Cases'.*? yAxis:.*?data:.*?\[([\d|null,]*)\]?", as_str, re.DOTALL)[0].split(',')

        for idx in range(len(daily_new_cases_data)):
            try:
                daily_new_cases_data[idx] = int(daily_new_cases_data[idx])

            except Exception as e:
                daily_new_cases_data[idx] = 0

        for idx in range(len(active_cases_data)):
            try:
                active_cases_data[idx] = int(active_cases_data[idx])

            except Exception as e:
                active_cases_data[idx] = 0

    return daily_new_cases_data, active_cases_data


def calculate_transmission_data(country_name, time_window=2):
    cases_path = Path(f'generated_data/cases/cases_{country_name}.json')

    if not cases_path.exists():
        daily_new_cases_data, active_cases_data = extract_case_numbers(country_name)
        country_cases_data = {'daily_new_cases': daily_new_cases_data, 'active_cases': active_cases_data}

        with cases_path.open('w') as f:
            json.dump(country_cases_data, f)

    else:
        with cases_path.open() as f:
            country_cases_data = json.load(f)
            daily_new_cases_data, active_cases_data = country_cases_data['daily_new_cases'], country_cases_data['active_cases']

    # daily_rates = []
    daily_cases = []  # smoothed

    for idx in range(time_window, len(daily_new_cases_data) - time_window):
        daily_cases_sum = 0.
        if time_window == 0:
            daily_cases.append(daily_new_cases_data[idx])
        else:
            for i in range(-time_window, time_window):
                daily_cases_sum += daily_new_cases_data[idx + i]
            average_case = daily_cases_sum / ((2 * time_window) + 1)
            daily_cases.append(average_case)

    dates = generate_past_dates(len(daily_cases), time_window)
    return daily_cases, dates


def aggregate_columns_max(s1, s2):
    return pd.concat([s1, s2], axis=1).max(axis=1)


def merge_country_dfs(df1, df2):  # Merge by maxing
    combined_df = df1.combine(df2, aggregate_columns_max)
    date_index = combined_df.columns.tolist().index('Date')
    cols = combined_df.columns.tolist()
    cols = cols[date_index:date_index + 1] + cols[:date_index] + cols[date_index + 1:]
    combined_df = combined_df[cols]

    return combined_df


if __name__ == '__main__':
    country_name = 'Germany'
    acaps_dfs = extract_acaps_measure_data()

    oxford_dfs = extract_oxford_measure_data()
    merge_country_dfs(acaps_dfs[country_name], oxford_dfs[country_name])
