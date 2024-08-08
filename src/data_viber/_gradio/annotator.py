# Copyright 2024-present, David Berenstein, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import List, Optional

import gradio

from data_viber._gradio.base import GradioDataCollectorInterface

_DEFAULT_COLORS = [
    "#a6cee3",
    "#1f78b4",
    "#b2df8a",
    "#33a02c",
    "#fb9a99",
    "#e31a1c",
    "#fdbf6f",
    "#ff7f00",
    "#cab2d6",
    "#6a3d9a",
    "#ffff99",
    "#b15928",
]


class GradioAnnotatorInterFace(GradioDataCollectorInterface):
    @classmethod
    def for_text_classification(
        cls,
        texts: List[str],
        labels: List[str],
        dataset_name: str,
        *,
        hf_token: Optional[str] = None,
        private: Optional[bool] = False,
    ):
        flagging_callback = cls._get_flagging_callback(
            dataset_name=dataset_name, hf_token=hf_token, private=private
        )

        def next_text(_):
            return texts.pop()

        input_text = gradio.TextArea(value=texts.pop(), label="Annotate")
        instance = cls(
            fn=next_text,
            inputs=[input_text],
            outputs=[input_text],
            flagging_callback=flagging_callback,
            flagging_options=labels,
            allow_flagging="manual",
            submit_btn="🗑️ discard",
            clear_btn=None,
        )
        return cls._add_html_component_with_viewer(
            instance=instance,
            flagging_callback=flagging_callback,
            show_embedded_viewer=True,
        )

    @classmethod
    def for_token_classification(
        cls,
        texts: List[str],
        labels: List[str],
        dataset_name: str,
        *,
        hf_token: Optional[str] = None,
        private: Optional[bool] = False,
    ):
        if isinstance(labels, list):
            labels = {label: color for label, color in zip(labels, _DEFAULT_COLORS)}
        flagging_callback = cls._get_flagging_callback(
            dataset_name=dataset_name, hf_token=hf_token, private=private
        )

        def convert_to_tokens(text: str):
            return [(char, None) for char in text]

        input_text = gradio.HighlightedText(
            value=convert_to_tokens(texts.pop()),
            color_map=labels,
            label="Annotate",
            interactive=True,
            show_legend=False,
            # combine_adjacent=True,
            adjacent_separator="",
        )

        def next_input(_):
            if len(texts):
                return convert_to_tokens(texts.pop())
            else:
                raise gradio.Error("No data to annotate left")

        instance = cls(
            fn=next_input,
            inputs=[input_text],
            outputs=[input_text],
            flagging_callback=flagging_callback,
            allow_flagging="auto",
        )
        return cls._add_html_component_with_viewer(
            instance=instance,
            flagging_callback=flagging_callback,
            show_embedded_viewer=True,
        )

    @classmethod
    def for_question_answering(
        cls,
        questions: List[str],
        contexts: List[str],
        dataset_name: str,
        *,
        hf_token: Optional[str] = None,
        private: Optional[bool] = False,
    ):
        raise NotImplementedError

    @classmethod
    def for_chat_preference(cls):
        raise NotImplementedError
