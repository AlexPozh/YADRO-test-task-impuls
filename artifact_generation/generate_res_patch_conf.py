import logging
import json

from .base_generator import BaseGenerator

logger = logging.getLogger(__name__)

class ResPatchedConfGenerator(BaseGenerator):
    def __init__(self, input_file_path: str | list[str], output_file_path: str | list[str]):
        super().__init__(input_file_path, output_file_path)
        self.__conf_data = None
        self.__delta_data = None

    def _read_input_file(self):
        conf, delta = self.input_file_path

        with open(conf, "r", encoding="UTF-8") as conf_file, \
            open(delta, "r", encoding="UTF-8") as delta_file:
            self.__conf_data = json.load(conf_file)
            self.__delta_data = json.load(delta_file)

    def _write_output_file(self):
        with open(self.output_file_path, "w", encoding="UTF-8") as res_patched_conf_file:
            json.dump(self.__conf_data, res_patched_conf_file)

    def __add__parameters(self):
        new_parameters = {
            d["key"] : d["value"] for d in self.__delta_data["additions"]
        }
        self.__conf_data.update(new_parameters)

    def __remove_parameters(self):
        deleted_parameters = [
            param for param in self.__delta_data["deletions"]
        ]
        for del_param in deleted_parameters:
            self.__conf_data.pop(del_param)

    def __update_parameters(self):
        updated_parameters = {
           d["key"] : d["to"] for d in self.__delta_data["updates"]
        }
        self.__conf_data.update(updated_parameters)

    def generate(self):
        try:
            self._read_input_file()
            self.__add__parameters()
            self.__remove_parameters()
            self.__update_parameters()
            
            self._write_output_file()

            logger.info("Файл %s сгенерирован успешно.", self.output_file_path.split("/")[-1])
        except Exception as error:
            logger.exception("Во время работы программы произошла ошибка: %r", error)