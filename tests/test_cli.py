from click.testing import CliRunner
from pda_cli.cli import main


class TestCLI:
    def test_list_devices(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--list-devices"])
        assert result.exit_code == 0

    def test_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Real-time pitch detection CLI" in result.output

    def test_invalid_algo(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--algo", "invalid"])
        assert result.exit_code != 0
        assert "Invalid value" in result.output

    def test_algo_choices(self):
        runner = CliRunner()
        for algo in ["zcr", "acf", "yin", "mpm"]:
            result = runner.invoke(main, ["--algo", algo, "--help"])
            assert result.exit_code == 0
