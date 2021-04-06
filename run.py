
from matplotlib import pyplot as plt
import sys
sys.path.append('.')

import covid19poland as PL

level = 2
x = PL.covid_tests(level = level, offline = False, from_github=True)

fig, ax = plt.subplots(figsize=(8,6))
if level == 1:
    x['tests'] = x['tests'].cumsum()
    x.plot(x='date',y='tests',ax=ax)
else:
    x['tests'] = x.groupby('region')['tests'].cumsum()
    for label, df in x.groupby('region'):
        df.plot(x = 'date', y = 'tests', ax=ax, label=label)

plt.show()