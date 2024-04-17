import pytest
from command_prompt import Command1
from cluster_manager import Clusters

class MockClusters:
    def __init__(self):
        self.clusters_loaded = {"GenAI": ["OpenAI", "Sam Altman", "Mistral", "Hugging Face", "RAG"]}

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
def command1_instance(mock_prompt):
    mock_rosters_instance = MockRosters()
    mock_clusters_instance = MockClusters()
    return Command1(mock_rosters_instance)

def test_do_run_list_of_ints(command1_instance):
    assert command1_instance.do_run('')