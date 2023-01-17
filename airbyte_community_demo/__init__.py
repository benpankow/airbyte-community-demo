from dagster import (
    AssetKey,
    AssetSelection,
    Definitions,
    ScheduleDefinition,
    define_asset_job,
    file_relative_path,
)
from dagster._utils import file_relative_path
from dagster_airbyte import airbyte_resource, load_assets_from_airbyte_instance
from dagster_dbt import dbt_cli_resource, load_assets_from_dbt_project
from dagster_hex.resources import hex_resource
from dagster_snowflake import build_snowflake_io_manager
from dagster_snowflake_pandas import SnowflakePandasTypeHandler

from .assets.hex import build_hex_notebook_asset

snowflake_io_manager = build_snowflake_io_manager([SnowflakePandasTypeHandler()])

airbyte_instance = airbyte_resource.configured(
    {
        "host": "localhost",
        "port": "8000",
        "username": "airbyte",
        "password": {"env": "AIRBYTE_PASSWORD"},
    }
)

airbyte_assets = load_assets_from_airbyte_instance(
    airbyte_instance, connection_to_asset_key_fn=lambda c, n: AssetKey([c.name, n])
)

DBT_PROJECT_DIR = file_relative_path(__file__, "../airbyte_community_demo_dbt")

dbt_assets = load_assets_from_dbt_project(
    project_dir=DBT_PROJECT_DIR, profiles_dir=DBT_PROJECT_DIR, key_prefix="activity"
)

hex_notebook_asset = build_hex_notebook_asset(
    name="activity_dash",
    project_id="e5b3334f-c371-45e3-81fe-ffbde3ccbbd7",
    description="Hex user activity dashboard",
    depends_on=[AssetKey(["activity", "daily_activity"])],
)


update_dash_job = define_asset_job("update_activity_dash", selection=AssetSelection.all())
update_dash_schedule = ScheduleDefinition(job=update_dash_job, cron_schedule="*/10 * * * *")

defs = Definitions(
    assets=[airbyte_assets, hex_notebook_asset] + dbt_assets,
    resources={
        "dbt": dbt_cli_resource.configured(
            {
                "project_dir": DBT_PROJECT_DIR,
                "profiles_dir": DBT_PROJECT_DIR,
            }
        ),
        "hex": hex_resource.configured(
            {
                "api_key": {"env": "HEX_TOKEN"},
            }
        ),
    },
    jobs=[update_dash_job],
    schedules=[update_dash_schedule],
)
