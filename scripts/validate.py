#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт валидации структуры документа, таблиц, рисунков и обязательных фраз.
Сравнивает заголовки, наличие таблиц с проверкой структуры (колонки, заголовки), что таблицы не пустые и не содержат пустых ячеек.
наличие рисунков по подписям, а также обязательные фразы (глобальные и внутри разделов).
Использование: python validate.py <docx-файл> <yaml-файл>
"""

import sys
import yaml
from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

def get_elements(doc):
    elements = []
    body = doc.element.body
    for child in body:
        if child.tag == qn('w:p'):
            para = Paragraph(child, doc)
            elements.append({'type': 'paragraph', 'element': para, 'idx': len(elements)})
        elif child.tag == qn('w:tbl'):
            table = Table(child, doc)
            elements.append({'type': 'table', 'element': table, 'idx': len(elements)})
    return elements

def extract_headings(elements):
    style_map = {
        'Heading 1': 1,
        'Heading 2': 2,
        'Heading 3': 3,
        'Heading 4': 4,
        'Heading 5': 5,
        'Heading 6': 6,
    }
    headings = []
    for elem in elements:
        if elem['type'] == 'paragraph':
            para = elem['element']
            text = para.text.strip()
            if text and para.style.name in style_map:
                level = style_map[para.style.name]
                headings.append((level, text, elem['idx']))
    return headings

def build_section_ranges(headings):
    if not headings:
        return []

    root = []
    stack = []

    for level, title, idx in headings:
        node = {'level': level, 'title': title, 'start': idx, 'end': None, 'children': []}
        while stack and stack[-1][0] >= level:
            stack.pop()
        if stack:
            stack[-1][1]['children'].append(node)
        else:
            root.append(node)
        stack.append((level, node))

    def fill_ends(nodes, parent_end=None):
        for i, node in enumerate(nodes):
            if i + 1 < len(nodes):
                node['end'] = nodes[i+1]['start']
            else:
                node['end'] = parent_end if parent_end is not None else None
            if node['children']:
                fill_ends(node['children'], node['end'])

    fill_ends(root)
    return root

def find_text_in_section(section_node, elements, text):
    start = section_node['start']
    end = section_node['end'] if section_node['end'] is not None else len(elements)
    for elem in elements[start:end]:
        if elem['type'] == 'paragraph':
            if text.lower() in elem['element'].text.lower():
                return True
    for child in section_node['children']:
        if find_text_in_section(child, elements, text):
            return True
    return False

def find_table_in_section(section_node, elements, expected_columns):
    """
    Ищет в пределах секции таблицу с совпадающими заголовками (первая строка),
    сравнение без учёта регистра.
    Возвращает (found, has_data, has_empty_cells)
    - found: bool, найдена ли таблица с правильными заголовками
    - has_data: bool, есть ли строки данных (rows > 1)
    - has_empty_cells: bool, есть ли пустые ячейки в строках данных (после strip)
    """
    start = section_node['start']
    end = section_node['end'] if section_node['end'] is not None else len(elements)
    expected_lower = [col.lower() for col in expected_columns]
    for elem in elements[start:end]:
        if elem['type'] == 'table':
            table = elem['element']
            if table.rows:
                first_row = table.rows[0]
                actual_headers = [cell.text.strip() for cell in first_row.cells]
                actual_lower = [h.lower() for h in actual_headers]
                if len(actual_lower) == len(expected_lower) and actual_lower == expected_lower:
                    # Проверяем наличие данных
                    has_data = len(table.rows) > 1
                    # Проверяем пустые ячейки в строках данных (индекс > 0)
                    has_empty_cells = False
                    if has_data:
                        for row_idx in range(1, len(table.rows)):
                            row = table.rows[row_idx]
                            for cell in row.cells:
                                if not cell.text.strip():
                                    has_empty_cells = True
                                    break
                            if has_empty_cells:
                                break
                    return (True, has_data, has_empty_cells)
    for child in section_node['children']:
        found, has_data, has_empty_cells = find_table_in_section(child, elements, expected_columns)
        if found:
            return (True, has_data, has_empty_cells)
    return (False, False, False)

def find_image_in_section(section_node, elements):
    start = section_node['start']
    end = section_node['end'] if section_node['end'] is not None else len(elements)
    for elem in elements[start:end]:
        if elem['type'] == 'paragraph':
            para = elem['element']
            for run in para.runs:
                if run.element.find(qn('w:drawing')) is not None:
                    return True
                if run.element.find(qn('w:pict')) is not None:
                    return True
    for child in section_node['children']:
        if find_image_in_section(child, elements):
            return True
    return False

def compare_structure(docx_path, yaml_path):
    doc = Document(docx_path)
    elements = get_elements(doc)
    headings = extract_headings(elements)
    tree = build_section_ranges(headings)

    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    expected = []
    def collect(sections, parent_path=[]):
        for sec in sections:
            title = sec['title']
            level = sec['level']
            full = ' > '.join(parent_path + [title])
            tables = sec.get('tables', [])
            figures = sec.get('figures', [])
            mandatory_phrases = sec.get('mandatory_phrases', [])
            expected.append({
                'level': level,
                'full': full,
                'tables': tables,
                'figures': figures,
                'mandatory_phrases': mandatory_phrases
            })
            if 'subsections' in sec:
                collect(sec['subsections'], parent_path + [title])
    collect(data['sections'])

    actual_nodes = []
    def walk(node, path):
        full = ' > '.join(path + [node['title']])
        actual_nodes.append({
            'level': node['level'],
            'full': full,
            'node': node
        })
        for child in node['children']:
            walk(child, path + [node['title']])
    for node in tree:
        walk(node, [])

    # Проверка заголовков (без учёта регистра)
    missing = []
    extra = []
    expected_set = { (item['level'], item['full'].lower()) for item in expected }
    actual_set = { (item['level'], item['full'].lower()) for item in actual_nodes }
    missing = expected_set - actual_set
    extra = actual_set - expected_set

    # Проверка таблиц, рисунков и фраз
    table_errors = []
    figure_errors = []
    phrase_errors = []
    for exp_item in expected:
        found_node = None
        for act_item in actual_nodes:
            if act_item['level'] == exp_item['level'] and act_item['full'].lower() == exp_item['full'].lower():
                found_node = act_item
                break
        if not found_node:
            continue

        # Проверяем обязательные фразы внутри раздела
        for phrase in exp_item['mandatory_phrases']:
            if not find_text_in_section(found_node['node'], elements, phrase):
                phrase_errors.append(f"В разделе '{exp_item['full']}' не найдена фраза: '{phrase}'")

        # Проверяем таблицы
        for table_spec in exp_item['tables']:
            keyword = table_spec.get('keyword')
            columns = table_spec.get('columns', [])
            if keyword:
                if not find_text_in_section(found_node['node'], elements, keyword):
                    table_errors.append(f"В разделе '{exp_item['full']}' не найдена подпись таблицы с ключевым словом: '{keyword}'")
                else:
                    if columns:
                        found, has_data, has_empty_cells = find_table_in_section(found_node['node'], elements, columns)
                        if not found:
                            table_errors.append(f"В разделе '{exp_item['full']}' не найдена таблица с заголовками: {columns}")
                        else:
                            if not has_data:
                                table_errors.append(f"В разделе '{exp_item['full']}' таблица с заголовками {columns} не содержит строк данных (пустая)")
                            if has_empty_cells:
                                table_errors.append(f"В разделе '{exp_item['full']}' таблица с заголовками {columns} содержит пустые ячейки в строках данных")

        # Проверяем рисунки
        for figure_spec in exp_item['figures']:
            keyword = figure_spec.get('keyword')
            if keyword:
                if not find_text_in_section(found_node['node'], elements, keyword):
                    figure_errors.append(f"В разделе '{exp_item['full']}' не найдена подпись рисунка с ключевым словом: '{keyword}'")
                else:
                    if not find_image_in_section(found_node['node'], elements):
                        figure_errors.append(f"В разделе '{exp_item['full']}' не найдено изображение для подписи: '{keyword}'")

    # Глобальные обязательные фразы
    global_phrases = data.get('mandatory_texts', [])
    global_errors = []
    for phrase in global_phrases:
        found = False
        for elem in elements:
            if elem['type'] == 'paragraph' and phrase.lower() in elem['element'].text.lower():
                found = True
                break
        if not found:
            global_errors.append(f"Глобально не найдена фраза: '{phrase}'")

    # Вывод результатов
    if not missing and not extra and not table_errors and not figure_errors and not phrase_errors and not global_errors:
        print("✅ Все разделы, таблицы, рисунки и фразы соответствуют эталону.")
        return True

    if missing:
        print("❌ Отсутствуют следующие разделы (или не совпадают уровни):")
        for level, full_lower in sorted(missing):
            orig = None
            for item in expected:
                if item['level'] == level and item['full'].lower() == full_lower:
                    orig = item['full']
                    break
            print(f"   - [{level}] {orig if orig else full_lower}")
    if extra:
        print("⚠️  Обнаружены лишние разделы (не указаны в эталоне):")
        for level, full_lower in sorted(extra):
            orig = None
            for item in actual_nodes:
                if item['level'] == level and item['full'].lower() == full_lower:
                    orig = item['full']
                    break
            print(f"   - [{level}] {orig if orig else full_lower}")
    if global_errors:
        print("❌ Глобальные фразы не найдены:")
        for err in global_errors:
            print(f"   - {err}")
    if phrase_errors:
        print("❌ Ошибки в обязательных фразах разделов:")
        for err in phrase_errors:
            print(f"   - {err}")
    if table_errors:
        print("❌ Ошибки в таблицах:")
        for err in table_errors:
            print(f"   - {err}")
    if figure_errors:
        print("❌ Ошибки в рисунках:")
        for err in figure_errors:
            print(f"   - {err}")
    return False

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Использование: {sys.argv[0]} <docx-файл> <yaml-файл>")
        sys.exit(1)

    docx_path = sys.argv[1]
    yaml_path = sys.argv[2]

    success = compare_structure(docx_path, yaml_path)
    sys.exit(0 if success else 1)