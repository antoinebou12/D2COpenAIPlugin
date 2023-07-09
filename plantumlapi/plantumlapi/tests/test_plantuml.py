import pytest
import os

from plantumlapi import PlantUML

@pytest.fixture
def plantuml():
    return PlantUML(
        url="http://www.plantuml.com/plantuml/img/",
        basic_auth=None,
        form_auth=None,
        http_opts={},
        request_opts={},
    )

def test_get_url(plantuml):
    plantuml_text = "@startuml\nactor Bob\n@enduml"
    url = plantuml.get_url(plantuml_text)
    assert url.startswith("http://www.plantuml.com/plantuml/img/")

def test_process(plantuml):  # Changed from test_processes to test_process
    plantuml_text = "@startuml\nactor Bob\n@enduml"
    image_data = plantuml.process(plantuml_text)  # Changed from processes to process
    assert len(image_data) > 0

def test_process_file(plantuml):  # Changed from test_processes_file to test_process_file
    filename = "test.puml"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("@startuml\nactor Bob\n@enduml")
    outfile = "test.png"

    # Call with correct input
    success = plantuml.process_file(filename, outfile=outfile)  # Changed from processes_file to process_file
    assert success
    assert os.path.exists(outfile)

    # Clean up files after test is complete
    os.remove(filename)
    os.remove(outfile)
