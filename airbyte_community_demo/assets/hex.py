from typing import List

from dagster import (
    AssetKey,
    MetadataValue,
    OpExecutionContext,
    Output,
    RetryPolicy,
    asset,
)
from dagster_hex.ops import HexOutput
from dagster_hex.resources import HexResource


def build_hex_notebook_asset(
    name: str, project_id: str, description: str, depends_on: List[AssetKey] = None
):
    @asset(
        required_resource_keys={"hex"},
        compute_kind="hex",
        group_name="dashboards",
        name=name,
        description=description,
        non_argument_deps=frozenset(depends_on),
        retry_policy=RetryPolicy(max_retries=2, delay=15),
    )
    def hex_asset(context: OpExecutionContext):
        hex_resource: HexResource = context.resources.hex
        hex_output: HexOutput = hex_resource.run_and_poll(project_id=project_id, inputs=None)

        return Output(
            hex_output,
            metadata={
                "run_url": MetadataValue.url(hex_output.run_response["runUrl"]),
                "run_status_url": MetadataValue.url(hex_output.run_response["runStatusUrl"]),
                "trace_id": MetadataValue.text(hex_output.run_response["traceId"]),
                "run_id": MetadataValue.text(hex_output.run_response["runId"]),
                "elapsed_time": MetadataValue.int(hex_output.status_response["elapsedTime"]),
            },
        )

    return hex_asset
