import os
import pytest
from unittest.mock import mock_open, ANY

import medperf.config as config
from medperf.comms.interface import Comms
from medperf.tests.utils import rand_l
from medperf.utils import storage_path
from medperf.entities.benchmark import Benchmark
from medperf.tests.mocks.requests import benchmark_body


PATCH_BENCHMARK = "medperf.entities.benchmark.{}"


@pytest.fixture
def comms(mocker):
    comms = mocker.create_autospec(spec=Comms)
    mocker.patch.object(comms, "get_benchmark", side_effect=benchmark_body)
    mocker.patch.object(comms, "get_benchmark_models", return_value=[])
    return comms


@pytest.fixture
def no_local(mocker):
    mocker.patch("os.listdir", return_value=[])
    mocker.patch(PATCH_BENCHMARK.format("Benchmark.write"))


def test_get_benchmark_retrieves_benchmark_from_comms(mocker, no_local, comms):
    # Arrange
    spy = mocker.spy(comms, "get_benchmark")

    # Act
    uid = 1
    Benchmark.get(uid, comms)

    # Assert
    spy.assert_called_once_with(uid)


@pytest.mark.parametrize("uid", rand_l(1, 5000, 10))
def test_get_benchmark_retrieves_models_from_comms(mocker, no_local, comms, uid):
    # Arrange
    spy = mocker.spy(comms, "get_benchmark_models")

    # Act
    Benchmark.get(uid, comms)

    # Assert
    spy.assert_called_once_with(uid)


@pytest.mark.parametrize("benchmarks_uids", [rand_l(1, 500, 3)])
def test_get_benchmark_retrieves_local_benchmarks(mocker, comms, benchmarks_uids):
    # Arrange
    benchmarks_uids = [str(uid) for uid in benchmarks_uids]
    mocker.patch("os.listdir", return_value=benchmarks_uids)
    mocker.patch(PATCH_BENCHMARK.format("Benchmark.write"))
    spy = mocker.patch(
        PATCH_BENCHMARK.format("Benchmark._Benchmark__get_local_dict"), return_value={}
    )
    uid = benchmarks_uids[0]

    # Act
    Benchmark.get(uid, comms)

    # Assert
    spy.assert_called_once_with(uid)


@pytest.mark.parametrize("benchmarks_uids", [rand_l(1, 500, 3)])
def test_get_benchmark_force_update_reads_remote_benchmark(
    mocker, comms, benchmarks_uids
):
    # Arrange
    benchmarks_uids = [str(uid) for uid in benchmarks_uids]
    mocker.patch("os.listdir", return_value=benchmarks_uids)
    mocker.patch(PATCH_BENCHMARK.format("Benchmark.write"))
    spy = mocker.patch(
        PATCH_BENCHMARK.format("Benchmark._Benchmark__get_local_dict"), return_value={}
    )
    uid = benchmarks_uids[0]

    # Act
    Benchmark.get(uid, comms, force_update=True)

    # Assert
    spy.assert_not_called()


@pytest.mark.parametrize("uid", rand_l(1, 500, 3))
def test_get_local_dict_reads_expected_file(mocker, comms, uid):
    # Arrange
    uid = str(uid)
    mocker.patch("os.listdir", return_value=[uid])
    mocker.patch("yaml.safe_load", return_value={})
    spy = mocker.patch("builtins.open", mock_open())
    mocker.patch(PATCH_BENCHMARK.format("Benchmark.write"))
    exp_file = os.path.join(
        storage_path(config.benchmarks_storage), uid, config.benchmarks_filename
    )

    # Act
    Benchmark.get(uid, comms)

    # Assert
    spy.assert_called_once_with(exp_file, "r")


@pytest.mark.parametrize("data_prep", rand_l(1, 500, 2))
@pytest.mark.parametrize("model", rand_l(1, 500, 2))
@pytest.mark.parametrize("eval", rand_l(1, 500, 2))
def test_tmp_creates_and_writes_temporary_benchmark(mocker, data_prep, model, eval):
    # Arrange
    data_prep = str(data_prep)
    model = str(model)
    eval = str(eval)
    write_spy = mocker.patch(PATCH_BENCHMARK.format("Benchmark.write"))
    init_spy = mocker.spy(Benchmark, "__init__")

    # Act
    benchmark = Benchmark.tmp(data_prep, model, eval)

    # Assert
    init_spy.assert_called_once()
    write_spy.assert_called_once()
    assert benchmark.data_preparation == data_prep
    assert benchmark.reference_model == model
    assert benchmark.evaluator == eval


def test_benchmark_includes_reference_model_in_models(comms, no_local):
    # Act
    uid = 1
    benchmark = Benchmark.get(uid, comms)

    # Assert
    assert benchmark.reference_model in benchmark.models


@pytest.mark.parametrize("models", [rand_l(1, 5000, 4) for _ in range(5)])
def test_benchmark_includes_additional_models_in_models(
    mocker, comms, models, no_local
):
    # Arrange
    mocker.patch.object(comms, "get_benchmark_models", return_value=models)

    # Act
    uid = 1
    benchmark = Benchmark.get(uid, comms)

    # Assert
    assert set(models).issubset(set(benchmark.models))


def test_write_writes_to_expected_file(mocker):
    # Arrange
    uid = 1
    mocker.patch("os.listdir", return_value=[])
    mocker.patch("os.path.exists", return_value=True)
    open_spy = mocker.patch("builtins.open", mock_open())
    yaml_spy = mocker.patch("yaml.dump")
    exp_file = os.path.join(
        storage_path(config.benchmarks_storage), str(uid), config.benchmarks_filename
    )

    # Act
    benchmark = Benchmark(uid, {})
    benchmark.write()

    # Assert
    open_spy.assert_called_once_with(exp_file, "w")
    yaml_spy.assert_called_once_with(benchmark.todict(), ANY)
