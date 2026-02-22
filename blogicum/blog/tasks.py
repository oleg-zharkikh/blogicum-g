from celery import shared_task, group, chain, chord
from .tasks_dispatcher import register_task, run_task

import time
from pprint import pprint

# @shared_task
@register_task('run_rag_process')
def run_rag_process(user_input_data):

    results = []



    tasks_params = [
        # (prompt, model, server_url)
        ("Запрос к модели А", "gpt-4", "http://llm-server-1:8000"),
        ("Запрос к модели Б", "gpt-3.5", "http://llm-server-2:8000"),
    ]

    result = run_task('get_completion', args=tasks_params[0], kwargs={})
    results.append(result)
    result = run_task('get_completion', args=tasks_params[1], kwargs={})
    results.append(result)

    # # Создаем группу задач
    # task_group = group(
    #     run_task.s('llm.get_completion', args=params, kwargs={})
    #     for params in tasks_params
    # )

    # # Запускаем группу и ждем результаты
    # result_group = task_group.apply_async()

    # # Ждем завершения всех задач в группе
    # # timeout=None - ждать бесконечно, interval - как часто проверять
    # results = result_group.get(timeout=None, interval=1)
    
    # Обрабатываем результаты
    with open("D:/Dev/blogicum-g/log.txt", "a") as f:
        f.write(f'[{time.strftime("%H:%M:%S")}] RAG process got results:\n')
        pprint(results, f)
        
    # Здесь можно сохранить результаты в БД
    final_result = {
        'status': 'completed',
        'llm_results': results,
        'timestamp': time.time()
    }

    with open("D:/Dev/blogicum-g/log.txt", "a") as f:
        f.write(f'[{time.strftime("%H:%M:%S")}] RAG process finished\n')

    return final_result


    # with open("D:/Dev/blogicum-g/log.txt", "a") as f:
    #     f.write(f'запущен процесс RAG: {user_input_data=}\n')
    # time.sleep(60)
    # result = "Результат обработки RAG"
    # with open("D:/Dev/blogicum-g/log.txt", "a") as f:
    #     f.write(f'{result=}\n')
    # return result

# stats/tasks.py
# from celery import shared_task

# @shared_task
@register_task('run_statistical_analysis')
def run_statistical_analysis(data1, data2):
    with open("D:/Dev/blogicum-g/log.txt", "a") as f:
        f.write(f'stat analisys started ... params: {str(data1)} - {str(data2)}\n')
    time.sleep(60)
    result = {"status": "Анализ завершен"}
    with open("D:/Dev/blogicum-g/log.txt", "a") as f:
        f.write(f'stat analisys has done\n')
    return result


@register_task('get_completion')
def get_completion(prompt, model, server_url):
    """Заглушка для запроса к LLM

    Имитирует долгий запрос (60 секунд) и возвращает уникальный ID.
    """
    task_id = f"llm_{int(time.time())}_{hash(prompt) % 10000}"

    with open("D:/Dev/blogicum-g/log.txt", "a") as f:
        f.write(f'[{time.strftime("%H:%M:%S")}] get_completion started: {model} on {server_url}\n')
    time.sleep(60)
    with open("D:/Dev/blogicum-g/log.txt", "a") as f:
        f.write(f'[{time.strftime("%H:%M:%S")}] get_completion finished: {task_id}\n')
    return {
        'task_id': task_id,
        'prompt': prompt[:30] + '...',
        'model': model,
        'server': server_url,
        'timestamp': time.time()
    }



# @shared_task(bind=True, max_retries=3, default_retry_delay=60)
# def get_completion_with_retry(self, prompt, model, server_url):
#     """
#     Запрос к LLM с автоматическими повторными попытками
#     """
#     try:
#         # Ваш код запроса к LLM
#         task_id = f"llm_{int(time.time())}_{hash(prompt) % 10000}"
        
#         # Симулируем случайную ошибку для теста
#         import random
#         if random.random() < 0.3:  # 30% шанс ошибки
#             raise ConnectionError("Simulated LLM server error")
        
#         time.sleep(60)
#         return {'task_id': task_id, 'model': model}
    
#     except Exception as e:
#         # Логируем ошибку
#         with open("D:/Dev/blogicum-g/errors.txt", "a") as f:
#             f.write(f'[{time.strftime("%H:%M:%S")}] LLM error: {e}, retry {self.request.retries}\n')
        
#         # Повторяем попытку
#         raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))