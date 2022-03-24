"""Create custom method which includes carbon dioxide as a resource flow as
carbon dioxide sequestered."""

import lciafmt

method = lciafmt.Method.TRACI
df = lciafmt.get_mapped_method(method, ['Global warming'])

# source carbon dioxide flow metadata
rec = df[df['Flowable']=='Carbon dioxide'].to_dict('records')[0]

# replace data for resource flow
flow_dict = {'Flowable': 'Carbon dioxide',
             'Context': 'resource/air',
             'Characterization Factor': -1.0,
             'Flow UUID': '58b5cd90-8ba4-32ea-b4aa-3a3438ba8419'}
for k in flow_dict:
    if k in rec:
        rec[k] = flow_dict[k]

df = df.append(rec, ignore_index=True)
# parquet is stored in traci subfolder
lciafmt.util.store_method(df, method, name='WARM-GHGs')
