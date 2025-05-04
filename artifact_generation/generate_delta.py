import json
import logging
from pprint import pprint

from .base_generator import BaseGenerator

logger = logging.getLogger(__name__)

class DeltaGenerator(BaseGenerator):
    def __init__(self, input_file_path: str | list[str], output_file_path: str | list[str]):
        super().__init__(input_file_path, output_file_path)
        self.__conf_data = None
        self.__patched_conf_data = None
        self.__delta_data = {}

    def _read_input_file(self):
        conf, patched_conf = self.input_file_path

        with open(conf, "r", encoding="UTF-8") as conf_file, \
            open(patched_conf, "r", encoding="UTF-8") as patched_conf_file:
            self.__conf_data = json.load(conf_file)
            self.__patched_conf_data = json.load(patched_conf_file)

    def _write_output_file(self):
        with open(self.output_file_path, "w", encoding="UTF-8") as delta_file:
            json.dump(self.__delta_data, delta_file)
    
    def __find_additions(self):
        self.__delta_data["additions"] = [
           {
               "key": key,
               "value": value
           } 
           for key, value in self.__patched_conf_data.items() if key[:11] == "added_param"
        ]
    
    @staticmethod
    def __sort_by_param(param: str | dict[str, str]) -> int:
        if isinstance(param, dict):
            return int(param["key"][5:])
        else:
            return int(param[5:])
        
    def __find_updates(self):
        common_params = set(self.__conf_data).intersection(self.__patched_conf_data)
        self.__delta_data["updates"] = [
            {
                "key": param,
                "from": self.__conf_data[param],
                "to": self.__patched_conf_data[param]
            }
            for param in common_params if self.__conf_data[param] != self.__patched_conf_data[param]
        ]
        """
            Порядок ключей в списке "updates" идет в хаотичном порядке (из-за множества),
            но в приложении 5 к этому заданию они идут по порядку. Я не нашел информации,
            как нужно выводить данные, поэтому последую примеру в приложении 5 и просто отсортирую значения
        """
        self.__delta_data["updates"].sort(
            key=DeltaGenerator.__sort_by_param
        )

    def __find_deletions(self):
        unique_conf_params = set(self.__conf_data).difference(self.__patched_conf_data)
        self.__delta_data["deletions"] = list(sorted(unique_conf_params, key=DeltaGenerator.__sort_by_param))

    def generate(self):
        try:
            self._read_input_file()
            self.__find_additions()
            self.__find_deletions()
            self.__find_updates()

            self._write_output_file()

            logger.info("Файл %s сгенерирован успешно.", self.output_file_path.split("/")[-1])
        except Exception as error:
            logger.exception("Во время работы программы произошла ошибка: %r", error)