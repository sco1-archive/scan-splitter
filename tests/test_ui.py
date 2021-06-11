from pytest_mock import MockerFixture
from src import io, ui
from typer.testing import CliRunner

RUNNER = CliRunner()


def test_single_nofile_prompts(mocker: MockerFixture) -> None:  # noqa: D103
    mocker.patch.object(ui, "_prompt_for_file", autospec=True)
    mocker.patch.object(io, "file_split_pipeline")  # Don't run the pipeline

    result = RUNNER.invoke(ui.scansplitter_cli, ["single"])
    assert result.exit_code == 0
    ui._prompt_for_file.assert_called()


def test_single_file_no_prompt(mocker: MockerFixture) -> None:  # noqa: D103
    mocker.patch.object(ui, "_prompt_for_file", autospec=True)
    mocker.patch.object(io, "file_split_pipeline")  # Don't run the pipeline

    result = RUNNER.invoke(ui.scansplitter_cli, ["single", "--scan-filepath", "README.md"])
    assert result.exit_code == 0
    ui._prompt_for_file.assert_not_called()


def test_batch_nodir_prompts(mocker: MockerFixture) -> None:  # noqa: D103
    mocker.patch.object(ui, "_prompt_for_dir", autospec=True)
    mocker.patch.object(io, "batch_split_pipeline")  # Don't run the pipeline

    result = RUNNER.invoke(ui.scansplitter_cli, ["batch"])
    assert result.exit_code == 0
    ui._prompt_for_dir.assert_called()


def test_batch_dir_no_prompt(mocker: MockerFixture) -> None:  # noqa: D103
    mocker.patch.object(ui, "_prompt_for_dir", autospec=True)
    mocker.patch.object(io, "batch_split_pipeline")  # Don't run the pipeline

    result = RUNNER.invoke(ui.scansplitter_cli, ["batch", "--scan-dir", "."])
    assert result.exit_code == 0
    ui._prompt_for_dir.assert_not_called()


def test_aggregate_nodir_prompts(mocker: MockerFixture) -> None:  # noqa: D103
    mocker.patch.object(ui, "_prompt_for_dir", autospec=True)
    mocker.patch.object(io, "anthro_measure_aggregation_pipeline")  # Don't run the pipeline

    result = RUNNER.invoke(ui.scansplitter_cli, ["aggregate"])
    assert result.exit_code == 0
    ui._prompt_for_dir.assert_called()


def test_aggregate_dir_no_prompt(mocker: MockerFixture) -> None:  # noqa: D103
    mocker.patch.object(ui, "_prompt_for_dir", autospec=True)
    mocker.patch.object(io, "anthro_measure_aggregation_pipeline")  # Don't run the pipeline

    result = RUNNER.invoke(ui.scansplitter_cli, ["aggregate", "--anthro-dir", "."])
    assert result.exit_code == 0
    ui._prompt_for_dir.assert_not_called()
