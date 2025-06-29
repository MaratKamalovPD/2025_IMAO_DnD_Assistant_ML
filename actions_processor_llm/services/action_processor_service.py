# actions_processor_ms/services/action_processor_service.py

import json
import logging
import os
import sys
from google.protobuf import struct_pb2
from datetime import datetime
import time

# Получаем абсолютный путь к корневой директории проекта
project_root = os.path.dirname(os.path.dirname(__file__))

# Добавляем путь к protobuf и common в sys.path
sys.path.append(os.path.join(project_root, "protobuf"))
sys.path.append(os.path.join(project_root, "common"))

import actions_processor_llm_pb2_grpc as pb2_grpc
import actions_processor_llm_pb2 as pb2

from common import openrouter_utils
from actions_processor_llm.prompts import attack_parsing


logger = logging.getLogger(__name__)


class ActionProcessorService(pb2_grpc.ActionProcessorServiceServicer):
    def __init__(self):
        self.generator = openrouter_utils.DnDBattleGenerator()

    def ProcessActions(self, request: pb2.ActionList, context) -> struct_pb2.Struct:
        request_time = datetime.now()
        logger.info("Время получения запроса: %s", request_time.strftime("%Y-%m-%d %H:%M:%S"))
        logger.info("Получен запрос на обработку %d действий", len(request.actions))

        if not request.actions:
            context.set_code(3)  # INVALID_ARGUMENT
            context.set_details("Список действий пуст")
            return struct_pb2.Struct()

        json_data = [
            {"name": action.name, "value": action.value}
            for action in request.actions
        ]

        prompt = attack_parsing.parse_action_json_prompt(json_data)

        # Засекаем время до и после LLM-запроса
        llm_start_time = time.time()
        llm_response = self.generator.get_parsed_action_json(prompt)
        llm_duration = time.time() - llm_start_time

        logger.info("Ответ от LLM получен за %.3f секунд", llm_duration)

        if not llm_response or not llm_response.strip():
            context.set_code(13)  # INTERNAL
            context.set_details("LLM вернул пустой ответ")
            return struct_pb2.Struct()

        try:
            cleaned_response = (
                llm_response
                    .replace("json", "")
                    .replace("```", "")
                    .replace("\n", "")
                    .strip()
            )

            parsed_json = json.loads(cleaned_response)

        except json.JSONDecodeError as e:
            context.set_code(13)  # INTERNAL
            context.set_details(f"Ошибка парсинга JSON: {str(e)}")
            return struct_pb2.Struct()

        if not parsed_json:
            context.set_code(13)  # INTERNAL
            context.set_details("LLM вернул пустой JSON-объект")
            return struct_pb2.Struct()

        result = struct_pb2.Struct()

        if isinstance(parsed_json, list):
            result.update({"parsed_actions": parsed_json})
        else:
            result.update(parsed_json)

        return result