# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import os

import yaml

from hugegraph_llm.utils.log import log

dir_name = os.path.dirname
F_NAME = "config_prompt.yaml"
yaml_file_path = os.path.join(os.getcwd(), "src/hugegraph_llm/resources/demo", F_NAME)


class BasePromptConfig:
    PROMPT_KEYS = [
        "graph_schema", "extract_graph_prompt", "default_question",
        "custom_rerank_info", "answer_prompt", "keywords_extract_prompt",
        "text2gql_graph_schema", "gremlin_generate_prompt", "doc_input_text"
    ]

    # graph_schema: str = ''
    # extract_graph_prompt: str = ''
    # default_question: str = ''
    # custom_rerank_info: str = ''
    # answer_prompt: str = ''
    # keywords_extract_prompt: str = ''
    # text2gql_graph_schema: str = ''
    # gremlin_generate_prompt: str = ''
    # doc_input_text: str = ''

    def __init__(self):
        self.language = 'en'
        for key in self.PROMPT_KEYS:
            setattr(self, f"{key}_en", '')
            setattr(self, f"{key}_zh", '')
        self.ensure_yaml_file_exists()

    def set_language(self, lang: str):
        if lang in ['en', 'zh']:
            self.language = lang
        else:
            # Optionally log a warning or raise an error for unsupported languages
            log.warning(f"Unsupported language '{lang}' specified. Defaulting to 'en'.")
            self.language = 'en'

    @property
    def graph_schema(self):
        if self.language == 'zh':
            return getattr(self, 'graph_schema_zh', getattr(self, 'graph_schema_en', ''))
        return getattr(self, 'graph_schema_en', '')

    @property
    def extract_graph_prompt(self):
        if self.language == 'zh':
            return getattr(self, 'extract_graph_prompt_zh', getattr(self, 'extract_graph_prompt_en', ''))
        return getattr(self, 'extract_graph_prompt_en', '')

    @property
    def default_question(self):
        if self.language == 'zh':
            return getattr(self, 'default_question_zh', getattr(self, 'default_question_en', ''))
        return getattr(self, 'default_question_en', '')

    @property
    def custom_rerank_info(self):
        if self.language == 'zh':
            return getattr(self, 'custom_rerank_info_zh', getattr(self, 'custom_rerank_info_en', ''))
        return getattr(self, 'custom_rerank_info_en', '')

    @property
    def answer_prompt(self):
        if self.language == 'zh':
            return getattr(self, 'answer_prompt_zh', getattr(self, 'answer_prompt_en', ''))
        return getattr(self, 'answer_prompt_en', '')

    @property
    def keywords_extract_prompt(self):
        if self.language == 'zh':
            return getattr(self, 'keywords_extract_prompt_zh', getattr(self, 'keywords_extract_prompt_en', ''))
        return getattr(self, 'keywords_extract_prompt_en', '')

    @property
    def text2gql_graph_schema(self):
        if self.language == 'zh':
            return getattr(self, 'text2gql_graph_schema_zh', getattr(self, 'text2gql_graph_schema_en', ''))
        return getattr(self, 'text2gql_graph_schema_en', '')

    @property
    def gremlin_generate_prompt(self):
        if self.language == 'zh':
            return getattr(self, 'gremlin_generate_prompt_zh', getattr(self, 'gremlin_generate_prompt_en', ''))
        return getattr(self, 'gremlin_generate_prompt_en', '')

    @property
    def doc_input_text(self):
        if self.language == 'zh':
            return getattr(self, 'doc_input_text_zh', getattr(self, 'doc_input_text_en', ''))
        return getattr(self, 'doc_input_text_en', '')

    def ensure_yaml_file_exists(self):
        if os.path.exists(yaml_file_path):
            log.info("Loading prompt file '%s' successfully.", F_NAME)
            with open(yaml_file_path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
                if data:  # Ensure data is not None
                    # Load existing values from the YAML file into the class attributes
                    for key, value in data.items():
                        setattr(self, key, value)
        else:
            self.generate_yaml_file()
            log.info("Prompt file '%s' doesn't exist, create it.", yaml_file_path)

    def save_to_yaml(self):
        prompts_to_save = {}
        for key in self.PROMPT_KEYS:
            prompts_to_save[f"{key}_en"] = getattr(self, f"{key}_en", "")
            prompts_to_save[f"{key}_zh"] = getattr(self, f"{key}_zh", "")

        # Ensure directory exists before writing
        os.makedirs(os.path.dirname(yaml_file_path), exist_ok=True)

        with open(yaml_file_path, "w", encoding="utf-8") as file:
            yaml.dump(prompts_to_save, file, allow_unicode=True, default_flow_style=False, sort_keys=False, width=float("inf"))

    def generate_yaml_file(self):
        if os.path.exists(yaml_file_path):
            log.info("%s already exists, do you want to override with the default configuration? (y/n)", yaml_file_path)
            update = input()
            if update.lower() != "y":
                return
            self.save_to_yaml()
        else:
            self.save_to_yaml()
            log.info("Prompt file '%s' doesn't exist, create it.", yaml_file_path)

    def update_yaml_file(self):
        self.save_to_yaml()
        log.info("Prompt file '%s' updated successfully.", F_NAME)
