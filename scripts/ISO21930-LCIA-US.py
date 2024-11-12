"""
Generate method for ISO21930-LCIA-US
"""

import lciafmt
import yaml

m = 'ISO21930-LCIA-US.yaml'
with open(lciafmt.util.datapath / m) as f:
    file = yaml.safe_load(f)
version = file.get('version')

df = lciafmt.custom.generate_lcia_compilation(m)
name = df['Method'][0]
if version:
    name = f'{name}{version}'

lciafmt.util.store_method(df, method_id=None, name=name)
lciafmt.util.save_json(method_id=None, mapped_data=df, name=name)
df.to_excel(f'{lciafmt.util.OUTPUTPATH}/{name}.xlsx', index=False)
