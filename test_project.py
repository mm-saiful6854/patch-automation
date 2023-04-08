import project
import pytest





"""def test_read_file():
    pass"""


"""@pytest.mark.parametrize("mydict, expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (2, -2, 0)
])
def test_get_list_of_host_details(host_dict, expected):
    assert project.get_list_of_host_details(host_dict) == expected"""

'''
    perform unit test on this method is_valid_ip_address
'''
@pytest.mark.parametrize("ip, expected", [
    ("192.2.1.0",True),
    ("02-02-2023 00:00:00",False)

])
def test_is_valid_ip_address(ip, expected):
    assert project.is_valid_ip_address(ip) == expected



'''
    perform unit test on this method convert_time_string_into_unix_time
'''
@pytest.mark.parametrize("time_string, expected", [
    ("05-04-2023 10:00:00",1680667200000),
    ("02-02-2023 00:00:00",1675274400000)

])
def test_convert_time_string_into_unix_time(time_string, expected):
    assert project.convert_time_string_into_unix_time(time_string) == expected