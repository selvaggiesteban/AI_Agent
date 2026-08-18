from abc import ABC, abstractmethod

class BaseCrawler(ABC):
    def __init__(self, network_manager):
        self.network_manager = network_manager

    @abstractmethod
    def get_suggestions(self, keyword):
        pass

    @abstractmethod
    def search_serp(self, keyword):
        pass
