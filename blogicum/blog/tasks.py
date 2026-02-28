from celery import shared_task, group, chain, chord
import logging
from redis_semaphore import Semaphore
import time
from pprint import pprint
from redis import Redis


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
semaphore = Semaphore(Redis(), count=1, namespace='llm')


@shared_task(
    bind=True
)
def run_rag_process(self, pid):
    logging.info(f"[{pid}]: RAG started")
    result = get_completion('1', pid + 1)
    logging.info(f"[{pid}]: RAG finished")
    return result


def get_completion(prompt, id):
    """Заглушка для запроса к LLM

    Имитирует долгий запрос (60 секунд) и возвращает уникальный ID.
    Работа с семафором.
    """
    logging.info(f"[{id}]: waiting...")
    with semaphore:
        logging.info(f"[{id}]: start")
        time.sleep(30)
        logging.info(f"[{id}]: done")
    return {
        'id': id,
        'timestamp': time.time()
    }

