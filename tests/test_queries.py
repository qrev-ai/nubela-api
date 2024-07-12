import json
import os
from typing import Any

import pytest

from nubela_api import NubelaAPI, Profile, NubelaSettings
from nubela_api.models.response import ErrorResponse, Response

## Get the directory of the current file
dir_path = os.path.dirname(os.path.realpath(__file__))
example_dir = os.path.join(dir_path, "examples")
person_json = os.path.join(example_dir, "person_example.json")
error_json = os.path.join(example_dir, "error_example.json")


class CountingAPI(NubelaAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.count = 0

    def _get_response(self, params: dict[str, Any]) -> dict[str, Any]:
        self.count += 1
        return {}


@pytest.fixture
def success_api():
    with open(person_json, "r") as f:
        js = json.load(f)

    class SuccessAPI(CountingAPI):
        def _api_call(self, params: dict[str, Any]) -> dict[str, Any]:
            self.count += 1
            return js
    settings = NubelaSettings(api_key="test")
    return SuccessAPI(settings=settings)


@pytest.fixture
def error_api():
    with open(error_json, "r") as f:
        js = json.load(f)

    class ErrorAPI(CountingAPI):
        def _api_call(self, params: dict[str, Any]) -> dict[str, Any]:
            self.count += 1
            return js
    settings = NubelaSettings(api_key="test")
    return ErrorAPI(settings=settings)


def dict_compare(dict1, dict2):
    """
    Recursively compares two dictionaries for equivalence.

    Args:
    - dict1, dict2: Dictionaries to compare

    Returns:
    - True if dictionaries are equivalent, False otherwise
    """
    # Base case: if both are not dictionaries, compare directly
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return dict1 == dict2

    # Check if keys are the same
    if set(dict1.keys()) != set(dict2.keys()):
        return False

    # Recursively compare values
    for key in dict1:
        if not dict_compare(dict1[key], dict2[key]):
            return False

    return True


def test_success_api(success_api: CountingAPI):
    r = success_api.query_linkedin("https://www.linkedin.com/in/username")
    assert r.code == 200
    assert r.profile
    d1 = r.profile.model_dump(mode="json")
    d2 = Profile(**json.load(open(person_json, "r"))).model_dump(mode="json")
    assert dict_compare(d1, d2)


def test_success_api_cache(success_api: CountingAPI):
    r1 = success_api.query_linkedin("https://www.linkedin.com/in/username")
    r2 = success_api.query_linkedin("https://www.linkedin.com/in/username")
    assert r1.code == 200
    assert r2.code == 200
    assert success_api.count == 1
    assert r1.profile
    d1 = r1.profile.model_dump(mode="json")
    d2 = Profile(**json.load(open(person_json, "r"))).model_dump(mode="json")
    assert dict_compare(d1, d2)


def test_error_api(error_api: CountingAPI):
    r = error_api.query_linkedin("https://www.linkedin.com/in/username")
    assert r.code != 200
    assert r.error
    d1 = r.error.model_dump(mode="json")
    d2 = ErrorResponse(**json.load(open(error_json, "r"))).model_dump(mode="json")
    assert dict_compare(d1, d2)


def test_save_load_response(success_api: CountingAPI):
    r = success_api.query_linkedin("https://www.linkedin.com/in/username")

    js = r.model_dump(mode="json")
    r2 = Response(**js)
    js2 = r2.model_dump(mode="json")
    assert r2.code == 200
    assert dict_compare(js, js2)


if __name__ == "__main__":
    pytest.main([__file__])
