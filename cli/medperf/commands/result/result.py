import typer

import medperf.config as config
from medperf.decorators import clean_except
from medperf.commands.result.list import ResultsList
from medperf.commands.result.create import BenchmarkExecution
from medperf.commands.result.submit import ResultSubmission

app = typer.Typer()


def run_benchmark(benchmark_uid, data_uid, model_uid):
    comms = config.comms
    ui = config.ui
    comms.authenticate()
    BenchmarkExecution.run(benchmark_uid, data_uid, model_uid, comms, ui)
    ResultSubmission.run(benchmark_uid, data_uid, model_uid, comms, ui)
    ui.print("✅ Done!")


@app.command("create")
@clean_except
def create(
    benchmark_uid: int = typer.Option(
        ..., "--benchmark", "-b", help="UID of the desired benchmark"
    ),
    data_uid: str = typer.Option(
        ..., "--data_uid", "-d", help="Registered Dataset UID"
    ),
    model_uid: int = typer.Option(
        ..., "--model_uid", "-m", help="UID of model to execute"
    ),
):
    """Runs the benchmark execution step for a given benchmark, prepared dataset and model
    """
    run_benchmark(benchmark_uid, data_uid, model_uid)


@app.command("submit")
@clean_except
def submit(
    benchmark_uid: int = typer.Option(
        ..., "--benchmark", "-b", help="UID of the executed benchmark"
    ),
    data_uid: str = typer.Option(
        ..., "--data_uid", "-d", help="UID of the dataset used for results"
    ),
    model_uid: int = typer.Option(
        ..., "--model_uid", "-m", help="UID of the executed model"
    ),
):
    """Submits already obtained results to the server"""
    comms = config.comms
    ui = config.ui
    comms.authenticate()
    ResultSubmission.run(benchmark_uid, data_uid, model_uid, comms, ui)
    ui.print("✅ Done!")


@app.command("ls")
@clean_except
def list():
    """List results stored locally and remotely from the user"""
    comms = config.comms
    ui = config.ui
    comms.authenticate()
    ResultsList.run(comms, ui)
