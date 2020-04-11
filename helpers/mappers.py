def acaps_country_name_mapper(country_name):
    countries_map = {'USA': 'United States of America', 'UK': 'United Kingdom', 'South Korea': 'Korea Republic of', 'Russia': 'Russian Federation'}

    if country_name in countries_map:
        return countries_map[country_name]

    else:
        return country_name


def acaps_measure_mapper(measure_name):
    measure_map = {'limit public gatherings': 'Public Gathering Limitations',

                   'border checks': 'Quarantine',
                   'introduction of isolation and quarantine policies': 'Quarantine',
                   'health screenings in airports and border crossings': 'Quarantine',
                   'surveillance and monitoring': 'Quarantine',

                   'international flights suspension': 'Flight Restrictions',

                   'border closure': 'Border Closure',
                   'visa restrictions': 'Border Closure',
                   'complete border closure': 'Border Closure',

                   'public services closure': 'Public Services Closure',
                   'schools closure': 'School Closure',
                   'awareness campaigns': 'Awareness Campaigns',
                   'general recommendations': 'Awareness Campaigns',  # TODO sort this out

                   'partial lockdown': 'Partial Lockdown',
                   'domestic travel restrictions': 'Partial Lockdown',
                   'curfews': 'Partial Lockdown',
                   'full lockdown': 'Full Lockdown',

                   'requirement to wear protective gear in public': 'Protective Gear',
                   }

    if measure_name in measure_map:
        return measure_map[measure_name]

    else:
        return None
