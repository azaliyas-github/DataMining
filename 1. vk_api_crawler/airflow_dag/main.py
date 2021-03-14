from datetime import datetime

from airflow.models import DAG
from airflow.operators.bash import BashOperator

args = {
	"owner": "airflow",
	"retries": 1
}

with DAG("titanic_pivot", args, None) as dag:
	execute_jar = BashOperator(
		task_id = "execute_jar",
		depends_on_past = False,
		start_date = datetime(2020, 3, 14),
		dag = dag,
		bash_command = 'java -jar {{ conf["core"]["dags_folder"] }}/vk_api_crawler/vk_api_crawler.jar')
