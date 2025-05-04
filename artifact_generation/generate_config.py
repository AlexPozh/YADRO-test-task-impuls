import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING
import logging
from .base_generator import BaseGenerator

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element
    from xml.etree.ElementTree import ElementTree

logger = logging.getLogger(__name__)

class ConfigGenerator(BaseGenerator):
    def __init__(self, input_file_path: str | list[str], output_file_path: str | list[str]):
        super().__init__(input_file_path, output_file_path)
        self.__doc = None  # file obj
        self.__data = None
        self.__children = {}

    def _read_input_file(self):
        self.__doc = ET.parse(self.input_file_path)

    def _write_output_file(self, tree: "ElementTree"):
        tree.write(self.output_file_path, encoding="utf-8")

    def __find_root_element(self):
        attrs = []
        for class_el in self.__doc.findall("Class"):
            if class_el.get("isRoot") == "true":
                self.root = class_el.get("name")
                for attr in class_el.findall("Attribute"):
                    attrs.append(
                        (attr.get("name"), attr.get("type"))
                    )
                self.__data = {
                    self.root: {
                        "attributes": attrs,
                        "children": {}
                    }
                }
                break
    
    def __find_child_elements(self):
        attrs = []
        for class_el in self.__doc.findall("Class"):
            if class_el.get("isRoot") == "false":
                
                for attr in class_el.findall("Attribute"):
                    attrs.append(
                        (attr.get("name"), attr.get("type"))
                    )
                self.__children[class_el.get("name")] = {
                        "attributes": attrs,
                        "children": {}
                    }
            attrs = []

    def __find_class_aggreg(self):
        for aggreg_el in self.__doc.findall("Aggregation"):
            target_class = aggreg_el.get("target")
            source_class = aggreg_el.get("source")
            
            if target_class == self.root:
                self.__data[self.root]["children"][source_class] = self.__children.get(source_class)

            else:
                self.__children[target_class]["children"][source_class] = self.__children.get(source_class)

    def __process_children(self, root: "Element", class_el: str, value: dict[str, list | dict]):
        node = ET.SubElement(root, class_el)
        if value["attributes"]:
            for attr in value["attributes"]:
                ET.SubElement(node, attr[0]).text = attr[1]

        elif value["children"]:
            for child, value in value["children"].items():
                self.__process_children(
                    root=node,
                    class_el=child,
                    value=value
                )
        else:
            # данный пробел нужен для того, чтобы библиотека xml создала пару тегов, 
            # а не один закрывающий тег. Например, тег <COMM> </COMM>, который не содержит 
            # внутри себя ничего, создался бы в виде <COMM/>, что тоже верно. 
            # Однако я решил сделать как в примере, поэтому пришлось добавить какое-то содержимое
            node.text = " " 
            return
        
    def generate(self):
        try:
            self._read_input_file()
            self.__find_root_element()
            self.__find_child_elements()
            self.__find_class_aggreg()
            
            # root tag
            root = ET.Element(self.root)

            # root attributes
            for attr in self.__data[self.root]["attributes"]:
                ET.SubElement(root, attr[0]).text = attr[1]
            
            # add other node/classes and their attrs
            for class_el, value in self.__data[self.root]["children"].items():
                self.__process_children(
                    root=root,
                    class_el=class_el,
                    value=value
                )
            tree = ET.ElementTree(root)

            self._write_output_file(tree)

            logger.info("Файл %s сгенерирован успешно.", self.output_file_path.split("/")[-1])
            
        except Exception as error:
            logger.exception("Во время работы программы произошла ошибка: %r", error)
