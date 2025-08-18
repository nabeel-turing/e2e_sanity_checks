import sanity_orchestrator_with_download as orchestrator
from datetime import datetime
import pandas as pd
try:
    start_time = datetime.now()
    run_name = f'sanity_check_{start_time.strftime("%Y%m%d_%H%M%S")}'
    run_identifiers = list(set(pd.read_csv("execution_configs.csv")['batch_id']))
    orchestrator.run_orchestration(run_name, run_identifiers)
    print(f"Finished Docker Run. Time Taken: {(datetime.now()-start_time).seconds} Seconds")
except (FileNotFoundError, FileExistsError, ConnectionError) as e:
    print(f"\\n❌ A critical error occurred: {e}")