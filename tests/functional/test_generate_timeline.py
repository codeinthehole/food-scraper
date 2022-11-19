import json

import time_machine

import main


def test_creates_timeline_doc(runner, fixture_path, tmp_path, tmp_path_factory):
    # Create an archive file with a product with some prices
    archive_data = {
        "123": {
            "name": "Crisps",
            "prices": [
                {
                    "date": "2022-11-01",
                    "price": "3.00",
                },
                {
                    "date": "2022-11-05",
                    "price": "4.00",
                },
            ],
        },
        "124": {
            "name": "Eggs",
            "prices": [
                {
                    "date": "2022-10-20",
                    "price": "0.50",
                },
                {
                    "date": "2022-11-01",
                    "price": "0.60",
                },
            ],
        },
    }
    archive_file = tmp_path / "archive.json"
    archive_file.write_text(json.dumps(archive_data))

    # Create a throwaway folder to generate the timeline doc in.
    timeline_folder = tmp_path_factory.mktemp("docs")
    timeline_file = timeline_folder / "timeline.md"

    # Run command.
    with time_machine.travel("2022-11-10T14:00"):
        result = runner.invoke(
            main.cli,
            args=[
                "generate-timeline",
                str(archive_file),
                str(timeline_file),
            ],
        )
    assert result.exit_code == 0, result.exception

    # Check timeline file has been created.
    assert timeline_file.exists()

    # Check contents are correct.
    expected_contents = (
        "# Product price timeline\n"
        "## 2022-11-05\n"
        "- Crisps changed price from £3.00 to £4.00 (+33%)\n"
        "## 2022-11-01\n"
        "- Crisps added to archive - price is £3.00\n"
        "- Eggs changed price from £0.50 to £0.60 (+20%)\n"
        "## 2022-10-20\n"
        "- Eggs added to archive - price is £0.50\n"
    )
    with open(timeline_file) as f:
        assert f.read() == expected_contents
