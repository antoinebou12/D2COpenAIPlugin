import pytest
import os

from plantuml import PlantUML

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

def test_process(plantuml):
    plantuml_text = "@startuml\nactor Bob\n@enduml"
    image_data = plantuml.process(plantuml_text)
    assert len(image_data) > 0

def test_process_file(plantuml):
    filename = "test.puml"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("@startuml\nactor Bob\n@enduml")
    outfile = "test.png"

    # Call with correct input
    success = plantuml.process_file(filename, outfile=outfile)
    assert success
    assert os.path.exists(outfile)

    os.remove(filename)
    os.remove(outfile)
