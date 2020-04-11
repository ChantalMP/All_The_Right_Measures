import pandas as pd
from helpers.mappers import acaps_country_name_mapper, acaps_measure_mapper
from helpers.utils import generate_dates

if __name__ == '__main__':
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

    country_dfs = {}

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

        country_dfs[country] = country_df

    print('Finished')
