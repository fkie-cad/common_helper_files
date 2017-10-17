from common_helper_files import get_version_string_from_git


def test_get_version_string_from_git():
    result = get_version_string_from_git('.')
    assert type(result) == str
