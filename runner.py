import sanity_orchestrator_with_download as orchestrator
from datetime import datetime
import pandas as pd

orchestrator.DOCKER_IMAGE = 'gen-agents-auto-qc'
MODE = "Colab" # 'Colab' or 'Proto'

exec_config = pd.read_csv("execution_configs.csv")
run_identifiers = list(set(exec_config['batch_id']))
run_identifiers.sort()

try:
    start_time = datetime.now()
    run_name = f'sanity_check_{start_time.strftime("%Y%m%d_%H%M%S")}'
    orchestrator.run_orchestration(run_name, run_identifiers, MODE)
    print(f"Finished Docker Run. Time Taken: {(datetime.now()-start_time).seconds} Seconds")
except (FileNotFoundError, FileExistsError, ConnectionError) as e:
    print(f"\\n❌ A critical error occurred: {e}")