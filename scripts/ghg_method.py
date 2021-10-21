"""Create custom method separating Major GHGs from Other GHGs for use in USEEIO."""

import lciafmt

method = lciafmt.Method.TRACI
df = lciafmt.get_mapped_method(method, ['Global warming'])

major_ghgs = ['Carbon dioxide', 'Methane', 'Nitrous oxide']

df.loc[df['Flowable'].isin(major_ghgs), 'Indicator'] = 'Global warming - Major GHGs'
df.loc[~df['Flowable'].isin(major_ghgs), 'Indicator'] = 'Global warming - Other GHGs'

# parquet is stored in traci subfolder
lciafmt.util.store_method(df, method, name='USEEIO-GHGs')
