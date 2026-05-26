import asyncio
from datetime import datetime, timedelta, timezone
from prefect.server.database.dependencies import provide_database_interface
from prefect.server.models import flow_runs, task_runs, logs
from prefect.server.schemas.filters import FlowRunFilter, TaskRunFilter, LogFilter, FlowRunFilterStartTime

async def cleanup_old_runs_and_logs(days=14):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    async with provide_database_interface() as session:
        # Delete old flow runs
        await flow_runs.delete_flow_runs(
            session=session,
            flow_run_filter=FlowRunFilter(start_time=FlowRunFilterStartTime(before=cutoff))
        )
        # Delete old task runs
        await task_runs.delete_task_runs(
            session=session,
            task_run_filter=TaskRunFilter(start_time=FlowRunFilterStartTime(before=cutoff))
        )
        # Delete old logs
        await logs.delete_logs(
            session=session,
            log_filter=LogFilter(timestamp=FlowRunFilterStartTime(before=cutoff))
        )
    print(f"Deleted Prefect runs/logs older than {days} days.")

if __name__ == "__main__":
    asyncio.run(cleanup_old_runs_and_logs(days=14))
