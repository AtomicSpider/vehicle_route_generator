from pathlib import Path
from io import StringIO
import pandas as pd
import re
import pickle

routes_dir = Path(r'routes').glob('**/*')
routes = [f for f in routes_dir if f.is_file()]
distances = dict()

for route in routes:
    try:
        with open(route, 'r') as f:
            data = f.readlines()[4:]

        distance = None

        try:
            match = re.search(r"(\d*\.)?\d+ km", data[1])
            distance = float(data[1][match.start():match.end() - 3])
            distances[route.stem] = distance
        except Exception as e:
            print(e)

        data = [','.join(line.split('\t')[1:3]) for line in data]
        df = pd.read_csv(StringIO('\n'.join(data)))
        df.to_csv('routes_cleaned/{}'.format(route.name), index=False)

        print('{}: SUCCESS, {} kms'.format(route.name, distance))

    except Exception as e:
        print('{}: {}'.format(route.name, e))

with open('distances.pickle', 'wb') as f:
    pickle.dump(distances, f, protocol=pickle.HIGHEST_PROTOCOL)
