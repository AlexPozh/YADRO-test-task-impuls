from abc import ABC, abstractmethod

class BaseGenerator(ABC):
    def __init__(self, input_file_paths: str | list[str], output_file_paths: str | list[str]):
        self.input_file_path = input_file_paths
        self.output_file_path = output_file_paths

    @abstractmethod
    def _read_input_file(self):
        pass
    
    @abstractmethod
    def _write_output_file(self):
        pass

    @abstractmethod
    def generate(self):
        pass