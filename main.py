import logging

from artifact_generation.generate_config import ConfigGenerator
from artifact_generation.generate_delta import DeltaGenerator
from artifact_generation.generate_meta import MetaGenerator
from artifact_generation.generate_res_patch_conf import ResPatchedConfGenerator

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(filename)s:%(funcName)s:%(lineno)d — %(message)s"
)

def main():
    conf_gen = ConfigGenerator(
        input_file_path="input/impulse_test_input.xml",
        output_file_path="out/config.xml")

    delt_gen = DeltaGenerator(
        input_file_path=[
                "input/config.json",
                "input/patched_config.json"
            ],
        output_file_path="out/delta.json"
    )

    meta_gen = MetaGenerator(
        input_file_path="input/impulse_test_input.xml",
        output_file_path="out/meta.json"
    )

    res_patch_conf = ResPatchedConfGenerator(
        input_file_path=[
            "input/config.json",
            "out/delta.json"
            ],
        output_file_path="out/res_patched_config.json"
    )
    
    conf_gen.generate()
    delt_gen.generate()
    meta_gen.generate()
    res_patch_conf.generate()
    
if __name__ == "__main__":
    main()