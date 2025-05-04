import xml.etree.ElementTree as ET
import logging
import json

from .base_generator import BaseGenerator

logger = logging.getLogger(__name__)

class MetaGenerator(BaseGenerator):
    def __init__(self, input_file_path: str | list[str], output_file_path: str | list[str]):
        super().__init__(input_file_path, output_file_path)
        self.__doc = None  # file obj
        self.__meta_data = {}
    
    def _read_input_file(self):
        self.__doc = ET.parse(self.input_file_path)

    def _write_output_file(self):
        with open(self.output_file_path, "w", encoding="UTF-8") as meta_file:
            json.dump(self.__meta_data, meta_file)

    def __find_class_attributes(self):
        for class_el in self.__doc.findall("Class"):
            name = class_el.get("name")
            isRoot = True if class_el.get("isRoot") == "true" else False
            documentation = class_el.get("documentation")
            parameters = []
            for attr in class_el.findall("Attribute"):
                parameters.append(
                    {
                        "name": attr.get("name"),
                        "type": attr.get("type")
                    }
                )
            self.__meta_data[name] = {
                    "class": name,
                    "documentation": documentation,
                    "isRoot": isRoot,
                    "parameters": parameters
                }
            
    def __add_multiplicity(self, class_el: str, class_multiplicity: str):
        try:
            min_multip, max_multip = class_multiplicity.split("..")
            self.__meta_data[class_el]["min"] = min_multip
            self.__meta_data[class_el]["max"] = max_multip
        except ValueError:
            self.__meta_data[class_el]["min"] = class_multiplicity
            self.__meta_data[class_el]["max"] = class_multiplicity
    
    def __find_class_aggreg_and_multiplicity(self):
        for aggreg_el in self.__doc.findall("Aggregation"):
            source_class = aggreg_el.get("source")
            target_class = aggreg_el.get("target")
            source_multi = aggreg_el.get("sourceMultiplicity")
            
            self.__add_multiplicity(source_class, source_multi) # min and max keys
            
            self.__meta_data[target_class]["parameters"].append(
                {
                    "name": source_class,
                    "type": "class"
                }
            )

    def generate(self):
        try:
            self._read_input_file()
            self.__find_class_attributes()
            self.__find_class_aggreg_and_multiplicity()

            self.__meta_data = list(self.__meta_data.values())
            
            self._write_output_file()
            logger.info("Файл %s сгенерирован успешно.", self.output_file_path.split("/")[-1])
        except Exception as error:
            logger.exception("Во время работы программы произошла ошибка: %r", error)