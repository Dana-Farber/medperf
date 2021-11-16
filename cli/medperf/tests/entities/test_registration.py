import os
import pytest
from unittest.mock import MagicMock
from pathlib import Path

import medperf
from medperf.ui import UI
from medperf.entities import Registration, Cube


out_path = "out_path"
patch_registration = "medperf.entities.registration.{}"
patch_cube = "medperf.entities.cube.{}"
reg_dict_keys = [
    "name",
    "description",
    "location",
    "split_seed",
    "data_preparation_mlcube",
    "generated_uid",
    "metadata",
    "status",
    "uid",
]


class MockedDataset:
    def __init__(self, uid, ui):
        self.registration = {"generated_uid": uid}


@pytest.fixture
def reg_init_params():
    cube = Cube(1, {"name": ""}, "")
    name = "mock registration"
    description = "mock_description"
    location = "mock location"
    return [cube, name, description, location]


@pytest.fixture
def reg_mocked_with_params(mocker, reg_init_params):
    mocker.patch(
        patch_registration.format("Registration._Registration__get_stats"),
        return_value={},
    )
    return reg_init_params


@pytest.mark.parametrize("mock_hash", ["hash1", "hash2", "hash3"])
def test_generate_uid_returns_folder_hash(mocker, mock_hash, reg_init_params):
    # Arrange
    mocker.patch(patch_registration.format("get_folder_sha1"), return_value=mock_hash)
    mocker.patch(
        patch_registration.format("Registration._Registration__get_stats"),
        return_value={},
    )

    # Act
    registration = Registration(*reg_init_params)
    gen_hash = registration.generate_uid(out_path)

    # Assert
    assert gen_hash == mock_hash


@pytest.mark.parametrize("path", ["stats_path", "./workspace/outputs/statistics.yaml"])
def test_get_stats_opens_stats_path(mocker, path, reg_init_params):
    # Arrange
    spy = mocker.patch("builtins.open", MagicMock())
    mocker.patch(patch_cube.format("Cube.get_default_output"), return_value=path)
    mocker.patch(patch_registration.format("yaml.full_load"), return_value={})

    # Act
    Registration(*reg_init_params)

    # Assert
    spy.assert_called_once_with(path, "r")


@pytest.mark.parametrize("stats", [{}, {"test": ""}, {"mean": 8}])
def test_get_stats_returns_stats(mocker, stats, reg_init_params):
    # Arrange
    mocker.patch("builtins.open", MagicMock())
    mocker.patch(patch_cube.format("Cube.get_default_output"), return_value="")
    mocker.patch(patch_registration.format("yaml.full_load"), return_value=stats)

    # Act
    registration = Registration(*reg_init_params)

    # Assert
    assert registration.stats == stats


def test_todict_returns_expected_keys(mocker, reg_mocked_with_params):
    # Act
    registration = Registration(*reg_mocked_with_params)

    # Assert
    assert set(registration.todict().keys()) == set(reg_dict_keys)


@pytest.mark.parametrize(
    "inputs", [["name", "desc", "loc"], ["chex", "chex dset", "col"]]
)
def test_retrieve_additional_data_prompts_user_correctly(
    mocker, ui, inputs, reg_mocked_with_params
):
    # Arrange
    m = MagicMock(side_effect=inputs)
    mocker.patch.object(ui, "prompt", m)
    reg = Registration(*reg_mocked_with_params)

    # Act
    reg.retrieve_additional_data(ui)
    vals = [reg.name, reg.description, reg.location]

    # Assert
    assert vals == inputs


@pytest.mark.parametrize("out_path", ["./test", "~/.medperf", "./workspace"])
@pytest.mark.parametrize("uid", [0, 12, 432])
def test_to_permanent_path_returns_expected_path(
    mocker, out_path, uid, reg_mocked_with_params
):
    # Arrange
    mocker.patch("os.rename")
    expected_path = os.path.join(str(Path(out_path).parent), str(uid))
    reg = Registration(*reg_mocked_with_params)
    reg.generated_uid = uid

    # Act
    new_path = reg.to_permanent_path(out_path)

    # Assert
    assert new_path == expected_path


@pytest.mark.parametrize(
    "out_path", ["test", "out", "out_path", "~/.medperf/data/tmp_0"]
)
@pytest.mark.parametrize("new_path", ["test", "new", "new_path", "~/.medperf/data/34"])
def test_to_permanent_path_renames_folder_correctly(
    mocker, out_path, new_path, reg_mocked_with_params
):
    # Arrange
    spy = mocker.patch("os.rename")
    mocker.patch("os.path.join", return_value=new_path)
    reg = Registration(*reg_mocked_with_params)
    reg.generated_uid = 0

    # Act
    reg.to_permanent_path(out_path)

    # Assert
    spy.assert_called_once_with(out_path, new_path)


@pytest.mark.parametrize("filepath", ["filepath"])
def test_write_writes_to_desired_file(mocker, filepath, reg_mocked_with_params):
    # Arrange
    spy = mocker.patch("os.path.join", return_value=filepath)
    mocker.patch("builtins.open", MagicMock())
    mocker.patch("yaml.dump", MagicMock())
    reg = Registration(*reg_mocked_with_params)

    # Act
    path = reg.write("")

    # Assert
    assert path == filepath


def test_is_registered_fails_when_uid_not_generated(mocker, ui, reg_mocked_with_params):
    # Arrange
    spy = mocker.spy(medperf.entities.registration, "pretty_error")
    mocker.patch.object(ui, "print_error")
    mocker.patch("medperf.utils.cleanup")
    reg = Registration(*reg_mocked_with_params)

    # Act
    with pytest.raises(SystemExit):
        reg.is_registered(ui)

    # Assert
    spy.assert_called_once()


def test_is_registered_retrieves_local_datasets(mocker, ui, reg_mocked_with_params):
    # Arrange
    spy = mocker.patch(patch_registration.format("Dataset.all"), return_values=[])
    reg = Registration(*reg_mocked_with_params)
    reg.generated_uid = 1

    # Act
    reg.is_registered(ui)

    # Assert
    spy.assert_called_once()


@pytest.mark.parametrize("dset_uids", [[1, 2, 3], [], [23, 5, 12]])
@pytest.mark.parametrize("uid", [1, 2, 3, 4, 5, 6])
def test_is_registered_finds_uid_in_dsets(
    mocker, ui, dset_uids, uid, reg_mocked_with_params
):
    # Arrange
    dsets = [MockedDataset(dset_uid, ui) for dset_uid in dset_uids]
    mocker.patch(patch_registration.format("Dataset.all"), return_value=dsets)
    reg = Registration(*reg_mocked_with_params)
    reg.generated_uid = uid

    # Act
    registered = reg.is_registered(ui)

    # Assert
    assert registered == (uid in dset_uids)
