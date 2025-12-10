

def build_document_traversal(statistic_data, docs_data):
    """
    Строит полный граф трассировки документов через все этапы
    """
    graph = {
        'nodes': {},
        'edges': [],
        'stage_order': []
    }
    
    # Собираем все уникальные документы и их появление на этапах
    for stage_data in statistic_data:
        stage_name = stage_data['stage']
        graph['stage_order'].append(stage_name)
        
        for doc in stage_data['processed_documents']:
            doc_id = doc['id']
            node_key = f"{stage_name}_{doc_id}"
            
            # Добавляем узел, если его еще нет
            if node_key not in graph['nodes']:
                graph['nodes'][node_key] = {
                    'id': node_key,
                    'original_id': doc_id,
                    'stage': stage_name,
                    'refs': doc.get('ref', []),
                    'info': docs_data.get(doc_id, {})
                }
    
    # Строим связи между документами
    for stage_idx, stage_data in enumerate(statistic_data):
        stage_name = stage_data['stage']
        
        for doc in stage_data['processed_documents']:
            doc_id = doc['id']
            current_node_key = f"{stage_name}_{doc_id}"
            
            # Ищем источники на предыдущих этапах
            for ref_doc_id in doc.get('ref', []):
                if ref_doc_id:
                    # Ищем на каком этапе появился этот документ
                    for prev_stage_idx in range(stage_idx):
                        prev_stage = statistic_data[prev_stage_idx]
                        for prev_doc in prev_stage['processed_documents']:
                            if prev_doc['id'] == ref_doc_id:
                                prev_node_key = f"{prev_stage['stage']}_{ref_doc_id}"
                                
                                # Добавляем ребро
                                edge_id = f"{prev_node_key}_{current_node_key}"
                                graph['edges'].append({
                                    'id': edge_id,
                                    'from': prev_node_key,
                                    'to': current_node_key
                                })
                                break
    
    return graph


def calculate_node_positions(graph_data, stage_height=150):
    """
    Рассчитывает позиции узлов для иерархического отображения
    """
    # Группируем узлы по этапам
    nodes_by_stage = {}
    
    for node_key, node_data in graph_data['nodes'].items():
        stage = node_data['stage']
        if stage not in nodes_by_stage:
            nodes_by_stage[stage] = []
        nodes_by_stage[stage].append(node_data)
    
    # Присваиваем позиции
    positioned_nodes = []
    
    for stage_idx, stage_name in enumerate(graph_data['stage_order']):
        stage_nodes = nodes_by_stage.get(stage_name, [])
        x_spacing = 800 / max(len(stage_nodes), 1)
        
        for i, node in enumerate(stage_nodes):
            node['x'] = i * x_spacing - 400
            node['y'] = stage_idx * stage_height
            positioned_nodes.append(node)
    
    return positioned_nodes
