# actions_processor_ms/services/action_processor_service.py

import logging
import os
import sys
from google.protobuf import struct_pb2

# Получаем абсолютный путь к корневой директории проекта
project_root = os.path.dirname(os.path.dirname(__file__))


# Добавляем путь к protobuf в sys.path
sys.path.append(os.path.join(project_root, "protobuf"))

import actions_processor_llm_pb2_grpc as pb2_grpc
import actions_processor_llm_pb2 as pb2


logger = logging.getLogger(__name__)

class ActionProcessorService(pb2_grpc.ActionProcessorServiceServicer):
    def ProcessActions(self, request: pb2.ActionList, context) -> struct_pb2.Struct:
        logger.info("Получен запрос на обработку %d действий", len(request.actions))

        # Заглушка — генерируем пример JSON-ответа
        result = struct_pb2.Struct()
        result.update({
            "summary": f"Обработано {len(request.actions)} действий",
            "first_action_name": request.actions[0].name if request.actions else "none"
        })

        return result
