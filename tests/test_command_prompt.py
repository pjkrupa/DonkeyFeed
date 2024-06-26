import sys
import os
current_dir = os.path.dirname(os.path.realpath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '..', 'src'))
sys.path.append(src_dir)

import random
import pytest
from typing import List
from src.command_prompt import Command
from src.cluster_manager import Clusters
from unittest.mock import patch, MagicMock


class MockClusters:
    def __init__(self):
        self.clusters_loaded = {"GenAI": ["OpenAI", "Sam Altman", "Mistral", "Hugging Face", "RAG"]}

# i need a mock of a rosters class
class MockRosters:
    def __init__(self):
        self.rosters_loaded = {
            "general": [
                           {
                               "RSS feed name": "Peter Krupa dot lol",
                               "URL": "https://www.peterkrupa.lol/feed",
                               "keywords": [
                                   "ActivityPub",
                                   "HuggingFace",
                                   "the number seven"]
                           },
                           {
                               "RSS feed name": "Wired",
                               "URL": "https://www.wired.com/feed/rss",
                               "keywords": [
                                   "OpenAI",
                                   "ActivityPub",
                                   "Mastodon",
                                   "Microsoft",
                                   "HuggingFace"]
                           },
                           {
                                "RSS feed name": "Gizmodo",
                                "URL": "https://gizmodo.com/rss",
                                "keywords": [
                                    "Sam Altman",
                                    "Google",
                                    "OpenAI"]
                           }
                        ],
            "general2": [
                {
                    "RSS feed name": "Peter Krupa dot lol",
                    "URL": "https://www.peterkrupa.lol/feed",
                    "keywords": [
                        "ActivityPub",
                        "HuggingFace",
                        "the number seven"]
                },
                {
                    "RSS feed name": "Wired",
                    "URL": "https://www.wired.com/feed/rss",
                    "keywords": [
                        "OpenAI",
                        "ActivityPub",
                        "Mastodon",
                        "Microsoft",
                        "HuggingFace"]
                },
                {
                    "RSS feed name": "Gizmodo",
                    "URL": "https://gizmodo.com/rss",
                    "keywords": [
                        "Sam Altman",
                        "Google",
                        "OpenAI"]
                }
            ]
        }


@pytest.fixture
def mock_prompt():
    with patch('command_prompt.Command.prompt') as mock:
        yield mock

@pytest.fixture
def command_instance(mock_prompt):
    mock_rosters_instance = MockRosters()
    mock_clusters_instance = MockClusters()
    return Command(mock_rosters_instance, 'general', None)

@pytest.fixture
def commands_with_arguments(command_instance) -> List[str]:
    return command_instance.arg_commands

@pytest.fixture
def solo_commands(command_instance) -> List[str]:
    return command_instance.solo_commands

def test_check_solo_commands(command_instance, solo_commands):
    for command in solo_commands:
        assert command_instance.check_command(command) == (command, None)

def test_check_commands_with_args(command_instance, commands_with_arguments):
    for command in commands_with_arguments:
        test_command = command + ' arguments'
        assert command_instance.check_command(test_command) == (command, 'arguments')

def test_check_bad_command(command_instance):
    assert command_instance.check_command('blah blah blah') is False
    assert command_instance.check_command('run') is False

def test_strip_characters(command_instance):
    string = "strip this leave this."
    chars = "strip this"
    assert command_instance.strip_chars(string, chars) == 'leave this.'

def test_check_index_with_good_index(command_instance):
    for index in range(0, len(command_instance.rosters.rosters_loaded[command_instance.roster_name])):
        assert command_instance.check_index(index) is True

def test_check_index_with_bad_index(command_instance):
    assert command_instance.check_index(len(command_instance.rosters.rosters_loaded[command_instance.roster_name])+1) is False
    assert command_instance.check_index(-2) is False

def test_check_index_for_setting_global_index_variable(command_instance):
    assert command_instance.check_index(1) is True and command_instance.index == 1

def test_make_list_strs(command_instance):
    test_string1 = 'angle, 45, Log'
    test_string2 = 'off,red 34,OPenAI'
    command_instance.make_list_strs(test_string1)
    assert command_instance.keyword_list == ['angle', '45', 'Log']
    command_instance.make_list_strs(test_string2)
    assert command_instance.keyword_list == ['off', 'red 34', 'OPenAI']

def test_make_list_ints_with_valid_indexes(command_instance):
    test_string1 = '0, 1, 2'
    test_string2 = '0,1,2'
    command_instance.make_list_ints(test_string1)
    assert command_instance.index_list == [0, 1, 2]
    command_instance.make_list_ints(test_string2)
    assert command_instance.index_list == [0, 1, 2]

def test_make_list_ints_with_invalid_indexes(command_instance):
    test_strings = ['5,6,7', 'deck, of, cards', 'banana']
    for string in test_strings:
        assert command_instance.make_list_ints(string) is False

def test_set_roster_with_valid_roster_name(command_instance):
    test_string1 = 'general'
    test_string2 = 'general2'
    command_instance.set_roster(test_string1)
    assert command_instance.roster_name == 'general'
    command_instance.set_roster(test_string2)
    assert command_instance.roster_name == 'general2'

def test_set_roster_with_invalid_roster_name(command_instance):
    test_string1 = '--boink'
    assert command_instance.set_roster(test_string1) is False

# test_strings = ['', 'general2', 'new roster', 'cancel']
def test_roster_pick_with_no_roster_name(command_instance, monkeypatch):
    with patch('builtins.input', return_value=''):
        command_instance.roster_pick('message')
        assert command_instance.roster_name == 'general'

def test_roster_pick_with_valid_roster_name(command_instance, monkeypatch):
    with patch('builtins.input', return_value='general2'):
        command_instance.roster_pick('message')
        assert command_instance.roster_name == 'general2'

def test_roster_pick_with_new_roster_name(command_instance, monkeypatch):
    with patch('builtins.input', return_value='new roster'):
        command_instance.roster_pick('message')
        assert command_instance.roster_name == 'new roster'

def test_roster_pick_with_cancel(command_instance, monkeypatch):
    with patch('builtins.input', return_value='cancel'):
        unchanged_roster = command_instance.roster_name
        assert command_instance.roster_pick('message') is None
        assert unchanged_roster == command_instance.roster_name

def test_set_range_valid_input(command_instance):
    command_instance.set_range('0, 2')
    assert command_instance.index_list == [0, 1, 2]
    command_instance.set_range('0,2')
    assert command_instance.index_list == [0, 1, 2]

def test_set_range_invalid_input(command_instance):
    test_inputs = ['0,1,2,3', '4,1', '0,5']
    for string in test_inputs:
        assert command_instance.set_range(string) is False

def test_run_invalid_indexes(command_instance):
    assert command_instance.run(str(len(command_instance.rosters.rosters_loaded[command_instance.roster_name]) + 1)) is False

def test_run_valid_indexes(command_instance):
    command_instance.run('--0,2')
    assert (command_instance.index_list == [0, 1, 2]
            and command_instance.command == 'run')
    command_instance.run('0,1,2')
    assert (command_instance.index_list == [0, 1, 2]
            and command_instance.command == 'run')
    command_instance.run('0,2')
    assert (command_instance.index_list == [0, 2]
            and command_instance.command == 'run')

def test_remove_keywords_valid_index_number(command_instance, monkeypatch):
    with (patch('builtins.input', return_value='a, b, c')):
        command_instance.remove_keywords('2')
        assert (command_instance.keyword_list == ['c', 'b', 'a']
                and command_instance.command == 'remove keywords')

def test_remove_keywords_invalid_index_number(command_instance, monkeypatch):
    with patch('builtins.input', return_value='a, b, c'):
        assert (command_instance.remove_keywords('12') is False
                and command_instance.command is None)
        assert (command_instance.remove_keywords('abc') is False
                and command_instance.command is None)
        assert (command_instance.remove_keywords('1, 2, 3') is False
                and command_instance.command is None)

def test_cluster_with_cluster_loaded(command_instance, monkeypatch):
    with patch.object(command_instance, 'cluster_name', 'GenAI'):
        command_instance.cluster('list')
        assert command_instance.command == 'cluster list'

def test_cluster_no_cluster_loaded(command_instance, monkeypatch):
    with patch.object(command_instance, 'cluster_name', None):
        assert command_instance.cluster('list') is False


def test_cluster_new_valid_input(command_instance, monkeypatch):
    with patch.object(command_instance, 'cluster_name', 'GenAI'), \
            patch('builtins.input', side_effect=['valid cluster', 'bink, bonk, boink']):
        command_instance.cluster('new')
        assert command_instance.command == 'cluster new'
        assert command_instance.keyword_list == ['bink', 'bonk', 'boink']

# def test_cluster_new_invalid_input(command_instance, monkeypatch):
#     with patch.object(command_instance, 'cluster_name', 'GenAI'), \
#             patch('builtins.input', side_effect=['valid cluster', 'bink, bonk, boink']):
#         command_instance.cluster('new')

def test_delete_valid_args(command_instance):
    command_instance.delete('--0,2')
    assert (command_instance.command == 'delete'
            and command_instance.index_list == [0, 1, 2])
    command_instance.index_list = []
    command_instance.delete('0,1,2')
    assert (command_instance.index_list == [0, 1, 2]
            and command_instance.command == 'delete')
    command_instance.index_list = []
    command_instance.delete('1')
    assert (command_instance.index_list == [1]
            and command_instance.command == 'delete')

def test_delete_invalid_args(command_instance):
    test_strings = ['20', '12,3,89', '-1', '']
    for string in test_strings:
        assert (command_instance.delete(string) is False
                and command_instance.command is None)

def test_new_valid_input(command_instance, monkeypatch):
    with patch('builtins.input', side_effect=[
        'feed name',
        'https://www.example.com/',
        'keyword, keyword, keyword'
    ]):
        command_instance.new()
        assert command_instance.new_title == 'feed name'
        assert command_instance.new_url == 'https://www.example.com/'
        assert command_instance.keyword_list == ['keyword', 'keyword', 'keyword']
        assert command_instance.command == 'new'

def test_new_invalid_url(command_instance, monkeypatch):
    with patch('builtins.input', side_effect=[
        'feed name',
        'fart. com',  # <-- testing this invalid URL
        'https://www.example.com/',
        'keyword, keyword, keyword'
    ]):
        command_instance.new()
        assert command_instance.new_title == 'feed name'
        assert command_instance.new_url == 'https://www.example.com/'
        assert command_instance.keyword_list == ['keyword', 'keyword', 'keyword']
        assert command_instance.command == 'new'

def test_new_feed_name_cancel(command_instance, monkeypatch):
    with patch('builtins.input', side_effect=['cancel']):
        command_instance.new()
        assert command_instance.new_title is None
        assert command_instance.new_url is None
        assert command_instance.roster_name == 'general'
        assert command_instance.keyword_list == []
        assert command_instance.command == None

def test_new_url_cancel(command_instance, monkeypatch):
    with patch('builtins.input', side_effect=['feed name', 'cancel']):
        command_instance.new()
        assert command_instance.new_title is None
        assert command_instance.new_url is None
        assert command_instance.roster_name == 'general'
        assert command_instance.keyword_list == []
        assert command_instance.command == None

def test_add_keywords_valid_input(command_instance, monkeypatch):
    with patch('builtins.input', return_value='keyword, keyword, keyword'):
        command_instance.add_keywords('0')
        assert command_instance.keyword_list == ['keyword', 'keyword', 'keyword']

def test_add_keywords_invalid_input(command_instance, monkeypatch):
    with patch('builtins.input', return_value='keyword, keyword, keyword'):
        assert (command_instance.add_keywords('rex') is False
                and command_instance.keyword_list == [])

@patch('os.path.exists', return_value=True)
def test_import_valid_input_opml(mock_exists, command_instance):
    test_opml = ['test_file.xml', 'test_file.opml']
    for value in test_opml:
        with patch('builtins.input', return_value=value):
            command_instance.import_file()
            assert command_instance.command == 'import opml'
            assert command_instance.opml_path == value

@patch('os.path.exists', return_value=True)
def test_import_valid_input_csv(mock_exists, command_instance):
    with patch('builtins.input', return_value='test_file.csv'):
        command_instance.import_file()
        assert command_instance.command == 'import csv'
        assert command_instance.csv_path == 'test_file.csv'

@patch('os.path.exists', return_value=True)
def test_import_invalid_input(mock_exists, command_instance):
    with patch('builtins.input', return_value='test_file.txt'):
        assert command_instance.import_file() is False

@patch('os.path.exists', return_value=False)
def test_import_bad_path(mock_exists, command_instance):
    with patch('builtins.input', return_value='test_file.csv'):
        assert command_instance.import_file() is False

def test_export_valid_input(command_instance):
    pass

@pytest.mark.parametrize("input_string", [
    'run 0',
    'run --general 0',
    'run 0,1',
    'run --0,2'
])
def test_prompt_valid_command(monkeypatch, input_string):
    mock_rosters = MockRosters()
    with patch('builtins.input', return_value=input_string):
        command_instance = Command(mock_rosters, 'general', 'GenAI')
        assert command_instance.prompt(command_instance.roster_name, 'GenAI') == 'run'

@pytest.mark.parametrize("input_string", [
    'runk 0',
    'run'
])
def test_prompt_invalid_command(monkeypatch, input_string):
    mock_rosters = MockRosters()
    with patch('builtins.input', return_value=input_string):
        command_instance = Command(mock_rosters, 'general', 'GenAI')
        assert command_instance.prompt(command_instance.roster_name, 'GenAI') is False

@patch('command_prompt.Command.new')
def test_prompt_response_new(mock_new, monkeypatch):
    mock_rosters = MockRosters()
    with patch('builtins.input', return_value='new'):
        command_instance = Command(mock_rosters, 'general', 'GenAI')
        assert command_instance.prompt(command_instance.roster_name, 'GenAI') == 'new'

def test_prompt_response_list(monkeypatch):
    mock_rosters = MockRosters()
    with patch('builtins.input', return_value='list'):
        command_instance = Command(mock_rosters, 'general', 'GenAI')
        assert command_instance.prompt(command_instance.roster_name, 'GenAI') == 'list'
    with patch('builtins.input', return_value='exit'):
        command_instance = Command(mock_rosters, 'general', 'GenAI')
        assert command_instance.prompt(command_instance.roster_name, 'GenAI') == 'exit'

def test_prompt_response_exit(monkeypatch):
    mock_rosters = MockRosters()
    with patch('builtins.input', return_value='exit'):
        command_instance = Command(mock_rosters, 'general','GenAI')
        assert command_instance.prompt(command_instance.roster_name, 'GenAI') == 'exit'

def test_prompt_response_help(monkeypatch):
    mock_rosters = MockRosters()
    with patch('builtins.input', return_value='help'):
        command_instance = Command(mock_rosters, 'general','GenAI')
        assert command_instance.prompt(command_instance.roster_name,'GenAI') == 'help'

def test_prompt_response_import(monkeypatch):
    mock_rosters = MockRosters()
    with patch('builtins.input', return_value='import'):
        command_instance = Command(mock_rosters, 'general', 'GenAI')
        assert command_instance.prompt(command_instance.roster_name, 'GenAI') == 'import'

def test_prompt_response_new_roster(monkeypatch):
    mock_rosters = MockRosters()
    with patch('builtins.input', return_value='new roster'):
        command_instance = Command(mock_rosters, 'general', 'GenAI')
        assert command_instance.prompt(command_instance.roster_name, 'GenAI') == 'new roster'

