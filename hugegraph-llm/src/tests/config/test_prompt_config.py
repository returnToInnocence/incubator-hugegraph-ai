# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from unittest.mock import patch, PropertyMock
import os

# Ensure the correct path is used for imports if tests are run from a different CWD
import sys
# Assuming the tests might be run from /app or /app/hugegraph-llm
# Add /app/hugegraph-llm/src to sys.path for hugegraph_llm imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from hugegraph_llm.config.prompt_config import PromptConfig
from hugegraph_llm.config.models.base_prompt_config import BasePromptConfig

# Define a dummy YAML content that might be loaded for more robust testing if needed,
# but mocking ensure_yaml_file_exists avoids this.
DUMMY_YAML_CONTENT = {
    "graph_schema_en": "English graph schema",
    "graph_schema_zh": "中文图谱模式",
    "extract_graph_prompt_en": "English extract graph prompt",
    # Deliberately missing extract_graph_prompt_zh to test fallback
    "default_question_en": "English default question",
    "default_question_zh": "中文默认问题",
}

class TestBasePromptConfigLanguageSwitch(unittest.TestCase):

    @patch.object(BasePromptConfig, 'ensure_yaml_file_exists')
    def setUp(self, mock_ensure_yaml):
        """Setup method to create a BasePromptConfig instance with mocked file I/O."""
        self.base_config = BasePromptConfig()
        # Mock the direct _en and _zh attributes as they are set in __init__
        # and would be loaded by ensure_yaml_file_exists if not mocked
        for key in BasePromptConfig.PROMPT_KEYS:
            setattr(self.base_config, f"{key}_en", f"Default English for {key}")
            setattr(self.base_config, f"{key}_zh", f"默认中文 {key}")

        # Override specific ones for targeted tests, simulating loaded values
        self.base_config.graph_schema_en = DUMMY_YAML_CONTENT["graph_schema_en"]
        self.base_config.graph_schema_zh = DUMMY_YAML_CONTENT["graph_schema_zh"]
        self.base_config.extract_graph_prompt_en = DUMMY_YAML_CONTENT["extract_graph_prompt_en"]
        # Ensure extract_graph_prompt_zh is not set on the instance to test fallback
        if hasattr(self.base_config, 'extract_graph_prompt_zh'):
             delattr(self.base_config, 'extract_graph_prompt_zh') # remove if BasePromptConfig init set it
        # For some keys, _zh might not be set by DUMMY_YAML_CONTENT, so BasePromptConfig's init default remains
        # e.g. default_question_en and default_question_zh are set by DUMMY_YAML_CONTENT
        self.base_config.default_question_en = DUMMY_YAML_CONTENT["default_question_en"]
        self.base_config.default_question_zh = DUMMY_YAML_CONTENT["default_question_zh"]


    @patch.object(BasePromptConfig, 'ensure_yaml_file_exists')
    def test_default_language_is_english(self, mock_ensure_yaml):
        config = BasePromptConfig() # ensure_yaml_file_exists is mocked
        self.assertEqual(config.language, 'en')
        # Test a property access
        # Temporarily set _en for a key to test property access without full setup
        config.graph_schema_en = "Test English Schema"
        self.assertEqual(config.graph_schema, "Test English Schema")

    def test_set_language_to_chinese(self):
        self.base_config.set_language('zh')
        self.assertEqual(self.base_config.language, 'zh')
        self.assertEqual(self.base_config.graph_schema, DUMMY_YAML_CONTENT["graph_schema_zh"])

    def test_set_language_to_english(self):
        self.base_config.set_language('zh') # Switch to zh first
        self.base_config.set_language('en') # Switch back to en
        self.assertEqual(self.base_config.language, 'en')
        self.assertEqual(self.base_config.graph_schema, DUMMY_YAML_CONTENT["graph_schema_en"])

    def test_fallback_to_english_if_chinese_prompt_missing(self):
        self.base_config.set_language('zh')
        # extract_graph_prompt_zh is deliberately not set in DUMMY_YAML_CONTENT or setUp for this instance
        self.assertEqual(self.base_config.extract_graph_prompt, DUMMY_YAML_CONTENT["extract_graph_prompt_en"])

    def test_unsupported_language_defaults_to_english(self):
        initial_graph_schema = self.base_config.graph_schema # Check current (en)
        self.base_config.set_language('fr') # Unsupported language
        self.assertEqual(self.base_config.language, 'en')
        self.assertEqual(self.base_config.graph_schema, initial_graph_schema)
        # Also check specific _en value
        self.assertEqual(self.base_config.graph_schema, DUMMY_YAML_CONTENT["graph_schema_en"])

    @patch.object(BasePromptConfig, 'ensure_yaml_file_exists')
    def test_direct_attribute_initialization_in_base_config(self, mock_ensure_yaml):
        # This tests that __init__ sets up _en and _zh attributes even before YAML load
        config = BasePromptConfig() # ensure_yaml_file_exists is mocked by class decorator
        for key in BasePromptConfig.PROMPT_KEYS:
            self.assertTrue(hasattr(config, f"{key}_en"), f"Missing {key}_en")
            self.assertTrue(hasattr(config, f"{key}_zh"), f"Missing {key}_zh")
            self.assertEqual(getattr(config, f"{key}_en"), '', f"{key}_en not empty")
            self.assertEqual(getattr(config, f"{key}_zh"), '', f"{key}_zh not empty")


class TestPromptConfigLanguageSwitchWithEnvVar(unittest.TestCase):

    @patch.object(PromptConfig, 'ensure_yaml_file_exists')
    def setUp(self, mock_ensure_yaml):
        # Specific setup for PromptConfig if it differs, though it inherits BasePromptConfig
        # For these tests, we rely on PromptConfig's actual default values for prompts
        pass

    @patch.object(PromptConfig, 'ensure_yaml_file_exists')
    @patch.dict(os.environ, {"HUGEGRAPH_PROMPT_LANGUAGE": "zh"})
    def test_language_set_to_chinese_by_env_var(self, mock_ensure_yaml):
        config = PromptConfig() # Reads env var in __init__ chain
        self.assertEqual(config.language, 'zh')
        # Check a prompt that has a Chinese version in PromptConfig's defaults
        # Assuming default_question_zh is defined in PromptConfig class
        self.assertEqual(config.default_question, config.default_question_zh)
        self.assertNotEqual(config.default_question, config.default_question_en,
                            "Should not be English if ZH is set by ENV and ZH default exists")


    @patch.object(PromptConfig, 'ensure_yaml_file_exists')
    @patch.dict(os.environ, {"HUGEGRAPH_PROMPT_LANGUAGE": "en"})
    def test_language_set_to_english_by_env_var(self, mock_ensure_yaml):
        config = PromptConfig()
        self.assertEqual(config.language, 'en')
        self.assertEqual(config.default_question, config.default_question_en)

    @patch.object(PromptConfig, 'ensure_yaml_file_exists')
    @patch.dict(os.environ, {"HUGEGRAPH_PROMPT_LANGUAGE": "fr"}) # Unsupported
    def test_language_defaults_to_english_for_unsupported_env_var(self, mock_ensure_yaml):
        config = PromptConfig()
        self.assertEqual(config.language, 'en')
        self.assertEqual(config.default_question, config.default_question_en)

    @patch.object(PromptConfig, 'ensure_yaml_file_exists')
    @patch.dict(os.environ, {}, clear=True) # Clear env var
    def test_language_defaults_to_english_if_env_var_not_set(self, mock_ensure_yaml):
        # Need to ensure that HUGEGRAPH_PROMPT_LANGUAGE might have been set by previous tests
        # or the environment itself.
        if "HUGEGRAPH_PROMPT_LANGUAGE" in os.environ:
             del os.environ["HUGEGRAPH_PROMPT_LANGUAGE"] # Ensure it's not set

        config = PromptConfig()
        self.assertEqual(config.language, 'en')
        self.assertEqual(config.default_question, config.default_question_en)


if __name__ == '__main__':
    unittest.main()
