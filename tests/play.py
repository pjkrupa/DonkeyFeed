from pathlib import Path
import datetime

root = Path(__file__).parent
date_and_time = datetime.datetime.now().strftime("%Y_%m_%d_%H%M")

string = date_and_time + '_' + 'test.txt'
save_path = root / string

with open(save_path, 'w') as f:
    f.write('Lets see if this works.')





