import re
import math
import copy


def find_direction(datum_json):
    # 0: up
    # 1: clockwised
    # 2: down
    # 3: counterclockwise

    vertices = datum_json['expense_json']['fullTextAnnotation']['pages'][0]['blocks'][0]['boundingBox']['vertices']
    if vertices[0]['x'] < vertices[1]['x'] and vertices[0]['y'] < vertices[3]['y']:
        return 0
    elif vertices[3]['x'] < vertices[0]['x'] and vertices[3]['y'] < vertices[2]['y']:
        return 1
    elif vertices[2]['x'] < vertices[3]['x'] and vertices[2]['y'] < vertices[1]['y']:
        return 2
    elif vertices[1]['x'] < vertices[2]['x'] and vertices[1]['y'] < vertices[0]['y']:
        return 3
    return 0


def pre_allocate(datum_json, direction):
    text_annotations = datum_json['expense_json']['textAnnotations']
    if direction == 0:
        return text_annotations
    neu_text_annotations = []
    for annotation in text_annotations:
        vertices = annotation['boundingPoly']['vertices']
        neu_vertices = ['none', 'none', 'none', 'none']
        for v, vertex in enumerate(vertices):
            neu_vertices[(v+direction)%4] = vertex
        annotation['boundingPoly']['vertices'] = neu_vertices
        neu_text_annotations.append(annotation)
    return neu_text_annotations


def pre_parse(datum_json, direction):
    text_annotations = pre_allocate(datum_json, direction)
    neu_text_annotations = []
    number_pattern = "[0-9]+"
    for annotation in text_annotations[1:]:
        description = annotation['description']
        bounding_poly = annotation['boundingPoly']
        search_results = re.findall(number_pattern, description)
        if search_results:
            for s, search_result in enumerate(search_results):
                span = re.search(search_result, description).span()
                left_description = description[:span[0]]
                mid_description = description[span[0]:span[1]]
                right_description = description[span[1]:]
                total_len = len(description)
                left_len = len(left_description)
                mid_len = len(mid_description)
                right_len = len(right_description)
                up_length = bounding_poly['vertices'][1]['x'] - bounding_poly['vertices'][0]['x']
                down_length = bounding_poly['vertices'][2]['x'] - bounding_poly['vertices'][3]['x']
                if left_len > 0:
                    # neu_bounding_poly = bounding_poly.copy()
                    neu_bounding_poly = copy.deepcopy(bounding_poly)
                    neu_bounding_poly['vertices'][1]['x'] = bounding_poly['vertices'][0]['x'] + up_length * (left_len/total_len)
                    neu_bounding_poly['vertices'][2]['x'] = bounding_poly['vertices'][3]['x'] + down_length * (left_len/total_len)
                    neu_text_annotations.append({'description': left_description, 'boundingPoly': neu_bounding_poly})
                if mid_len > 0:
                    # neu_bounding_poly = bounding_poly.copy()
                    neu_bounding_poly = copy.deepcopy(bounding_poly)
                    neu_bounding_poly['vertices'][0]['x'] = bounding_poly['vertices'][0]['x'] + up_length * (left_len/total_len)
                    neu_bounding_poly['vertices'][1]['x'] = bounding_poly['vertices'][0]['x'] + up_length * ((left_len+mid_len)/total_len)
                    neu_bounding_poly['vertices'][2]['x'] = bounding_poly['vertices'][3]['x'] + down_length * ((left_len+mid_len)/total_len)
                    neu_bounding_poly['vertices'][3]['x'] = bounding_poly['vertices'][3]['x'] + down_length * (left_len/total_len)
                    neu_text_annotations.append({'description': mid_description, 'boundingPoly': neu_bounding_poly})
                if s == len(search_results) - 1:
                    if right_len > 0:
                        # neu_bounding_poly = bounding_poly.copy()
                        neu_bounding_poly = copy.deepcopy(bounding_poly)
                        neu_bounding_poly['vertices'][0]['x'] = bounding_poly['vertices'][0]['x'] + up_length * ((left_len+mid_len)/total_len)
                        neu_bounding_poly['vertices'][3]['x'] = bounding_poly['vertices'][3]['x'] + down_length * ((left_len+mid_len)/total_len)
                else:
                    description = right_description
                    # neu_bounding_poly = bounding_poly.copy()
                    neu_bounding_poly = copy.deepcopy(bounding_poly)
                    neu_bounding_poly['vertices'][0]['x'] = bounding_poly['vertices'][0]['x'] + up_length * ((left_len+mid_len)/total_len)
                    neu_bounding_poly['vertices'][3]['x'] = bounding_poly['vertices'][3]['x'] + down_length * ((left_len+mid_len)/total_len)
                    bounding_poly = copy.deepcopy(neu_bounding_poly)
        else:
            neu_text_annotations.append(annotation)
    return neu_text_annotations


def find_up(vertices, text_annotations):
    neu_annotations = []
    x = (vertices[0]['x'] + vertices[2]['x']) / 2
    y = (vertices[0]['y'] + vertices[2]['y']) / 2
    for annotation in text_annotations:
        current_x = (annotation['boundingPoly']['vertices'][0]['x'] + annotation['boundingPoly']['vertices'][2]['x']) / 2
        current_y = (annotation['boundingPoly']['vertices'][0]['y'] + annotation['boundingPoly']['vertices'][2]['y']) / 2
        angle_radians = math.atan2(y - current_y, x - current_x)
        angle_degrees = math.degrees(angle_radians)
        if 20 <= angle_degrees <= 160:
            neu_annotations.append(annotation)

    closest_neighbour = {
        'description': 'None',
        'boundingPoly': {
            'vertices': [{'x': 0, 'y': 0}, {'x': 0, 'y': 0}, {'x': 0, 'y': 0}, {'x': 0, 'y': 0}]
        },
        'distance': 0.1,
        'angle': 0
    }

    for annotation in neu_annotations:
        current_x = (annotation['boundingPoly']['vertices'][0]['x'] + annotation['boundingPoly']['vertices'][2]['x']) / 2
        current_y = (annotation['boundingPoly']['vertices'][0]['y'] + annotation['boundingPoly']['vertices'][2]['y']) / 2
        distance = math.sqrt(((current_x-x)**2)+((current_y-y)**2))
        if 0 < distance < closest_neighbour['distance']:
            angle_radians = math.atan2(y - current_y, x - current_x)
            angle_degrees = math.degrees(angle_radians)
            closest_neighbour['distance'] = distance
            closest_neighbour['description'] = annotation['description']
            closest_neighbour['boundingPoly'] = annotation['boundingPoly']
            closest_neighbour['angle'] = angle_degrees

    return closest_neighbour


def find_down(vertices, text_annotations):
    neu_annotations = []
    x = (vertices[0]['x'] + vertices[2]['x']) / 2
    y = (vertices[0]['y'] + vertices[2]['y']) / 2
    for annotation in text_annotations:
        current_x = (annotation['boundingPoly']['vertices'][0]['x'] + annotation['boundingPoly']['vertices'][2]['x']) / 2
        current_y = (annotation['boundingPoly']['vertices'][0]['y'] + annotation['boundingPoly']['vertices'][2]['y']) / 2
        angle_radians = math.atan2(y - current_y, x - current_x)
        angle_degrees = math.degrees(angle_radians)
        if -160 <= angle_degrees <= -20:
            neu_annotations.append(annotation)

    closest_neighbour = {
        'description': 'None',
        'boundingPoly': {
            'vertices': [{'x': 0, 'y': 0}, {'x': 0, 'y': 0}, {'x': 0, 'y': 0}, {'x': 0, 'y': 0}]
        },
        'distance': 0.1,
        'angle': 0
    }

    for annotation in neu_annotations:
        current_x = (annotation['boundingPoly']['vertices'][0]['x'] + annotation['boundingPoly']['vertices'][2]['x']) / 2
        current_y = (annotation['boundingPoly']['vertices'][0]['y'] + annotation['boundingPoly']['vertices'][2]['y']) / 2
        distance = math.sqrt(((current_x-x)**2)+((current_y-y)**2))
        if 0 < distance < closest_neighbour['distance']:
            angle_radians = math.atan2(y - current_y, x - current_x)
            angle_degrees = math.degrees(angle_radians)
            closest_neighbour['angle'] = angle_degrees
            closest_neighbour['distance'] = distance
            closest_neighbour['description'] = annotation['description']
            closest_neighbour['boundingPoly'] = annotation['boundingPoly']

    return closest_neighbour


def find_right(vertices, text_annotations):
    neu_annotations = []
    x = (vertices[0]['x'] + vertices[2]['x']) / 2
    y = (vertices[0]['y'] + vertices[2]['y']) / 2
    for annotation in text_annotations:
        current_x = (annotation['boundingPoly']['vertices'][0]['x'] + annotation['boundingPoly']['vertices'][2]['x']) / 2
        current_y = (annotation['boundingPoly']['vertices'][0]['y'] + annotation['boundingPoly']['vertices'][2]['y']) / 2
        angle_radians = math.atan2(y - current_y, x - current_x)
        angle_degrees = math.degrees(angle_radians)
        if 160 <= angle_degrees or angle_degrees <= -160:
            neu_annotations.append(annotation)

    closest_neighbour = {
        'description': 'None',
        'boundingPoly': {
            'vertices': [{'x': 0, 'y': 0}, {'x': 0, 'y': 0}, {'x': 0, 'y': 0}, {'x': 0, 'y': 0}]
        },
        'distance': 0.1,
        'angle': 0
    }

    for annotation in neu_annotations:
        current_x = (annotation['boundingPoly']['vertices'][0]['x'] + annotation['boundingPoly']['vertices'][2]['x']) / 2
        current_y = (annotation['boundingPoly']['vertices'][0]['y'] + annotation['boundingPoly']['vertices'][2]['y']) / 2
        distance = math.sqrt(((current_x-x)**2)+((current_y-y)**2))
        if 0 < distance < closest_neighbour['distance']:
            angle_radians = math.atan2(y - current_y, x - current_x)
            angle_degrees = math.degrees(angle_radians)
            closest_neighbour['angle'] = angle_degrees
            closest_neighbour['distance'] = distance
            closest_neighbour['description'] = annotation['description']
            closest_neighbour['boundingPoly'] = annotation['boundingPoly']

    return closest_neighbour


def find_left(vertices, text_annotations):
    neu_annotations = []
    x = (vertices[0]['x'] + vertices[2]['x']) / 2
    y = (vertices[0]['y'] + vertices[2]['y']) / 2
    for annotation in text_annotations:
        current_x = (annotation['boundingPoly']['vertices'][0]['x'] + annotation['boundingPoly']['vertices'][2]['x']) / 2
        current_y = (annotation['boundingPoly']['vertices'][0]['y'] + annotation['boundingPoly']['vertices'][2]['y']) / 2
        angle_radians = math.atan2(y - current_y, x - current_x)
        angle_degrees = math.degrees(angle_radians)
        if -20 <= angle_degrees <= 20:
            neu_annotations.append(annotation)

    closest_neighbour = {
        'description': 'None',
        'boundingPoly': {
            'vertices': [{'x': 0, 'y': 0}, {'x': 0, 'y': 0}, {'x': 0, 'y': 0}, {'x': 0, 'y': 0}]
        },
        'distance': 0.1,
        'angle': 0
    }

    for annotation in neu_annotations:
        current_x = (annotation['boundingPoly']['vertices'][0]['x'] + annotation['boundingPoly']['vertices'][2]['x']) / 2
        current_y = (annotation['boundingPoly']['vertices'][0]['y'] + annotation['boundingPoly']['vertices'][2]['y']) / 2
        distance = math.sqrt(((current_x-x)**2)+((current_y-y)**2))
        if 0 < distance < closest_neighbour['distance']:
            angle_radians = math.atan2(y - current_y, x - current_x)
            angle_degrees = math.degrees(angle_radians)
            closest_neighbour['angle'] = angle_degrees
            closest_neighbour['distance'] = distance
            closest_neighbour['description'] = annotation['description']
            closest_neighbour['boundingPoly'] = annotation['boundingPoly']

    return closest_neighbour


def find_neigbours(vertices, text_annotations):
    neighbours = {
        'up': find_up(vertices, text_annotations),
        'down': find_down(vertices, text_annotations),
        'right': find_right(vertices, text_annotations),
        'left': find_left(vertices, text_annotations)
    }
    return neighbours


def normalize_coordinates(text_annotations):
    neu_annotations = []
    max_x = 0
    max_y = 0
    min_x = 9999999
    min_y = 9999999
    for annotation in text_annotations:
        vertices = annotation['boundingPoly']['vertices']
        for vertex in vertices:
            current_x = vertex['x']
            current_y = vertex['y']
            if current_y < min_y:
                min_y = current_y
            if current_y > max_y:
                max_y = current_y
            if current_x < min_x:
                min_x = current_x
            if current_x > max_x:
                max_x = current_x

    height = max_y - min_y
    width = max_x - min_x

    for annotation in text_annotations:
        neu_vertices = []
        for vertex in annotation['boundingPoly']['vertices']:
            neu_vertices.append({'x': (vertex['x'] - min_x) / width, 'y': (vertex['y'] - min_y) / height})
        neu_annotations.append({'description': annotation['description'], 'boundingPoly': {'vertices': neu_vertices}})

    return neu_annotations


def find_candidates(datum_json):
    direction = find_direction(datum_json)
    pattern = '^[0-9]{4}$'
    phone_pattern_left = '\('
    phone_pattern_right = "\)"
    candidates = []
    text_annotations = pre_parse(datum_json, direction)
    text_annotations = normalize_coordinates(text_annotations)
    for annotation in text_annotations:
        desription = annotation['description']
        if re.search(pattern, desription) or 'Kart' in desription or "KART" in desription or "Kredi" in desription or "KREDİ" in desription:
            candidate = {
                'neighbours': find_neigbours(annotation['boundingPoly']['vertices'], text_annotations),
                'annotation': annotation
            }
            if re.search(phone_pattern_left, candidate['neighbours']['left']['description']) and re.search(phone_pattern_right, candidate['neighbours']['right']['description']):
                continue
            candidates.append(candidate)
    return candidates
