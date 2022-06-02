import fasttext
import numpy as np
from flask import Flask, request
from payment_type_utils import find_candidates


app = Flask(__name__)

ft = fasttext.load_model('cc.tr.300.bin')


def convert_to_dict(r):
    r_length = len(r)
    output = {}
    for i in range(r_length):
        current = {}
        for j in range(len(r[i])):
            current[str(j)] = r[i][j]
        output[str(i)] = current
    return output


def convert_to_dict_payment_type(r):
    a_length = r.shape[0]
    b_length = r.shape[1]
    c_length = r.shape[2]
    candidates = {}
    for i in range(a_length):
        candidate = {}
        for j in range(b_length):
            current = {}
            for k in range(c_length):
                current[str(k)] = r[i][j][k]
            candidate[str(j)] = current
        candidates[str(i)] = candidate

    return candidates


def numpy_data(json_data, word_in_invoice=60):
    word_count = 0
    file_data = []
    annotations = json_data['textAnnotations']
    for annotation in annotations[1:]:
        try:
            text = annotation['description']
            for char in text:
                if 48 <= ord(char) <= 57:
                    continue
            b_box = []
            for bounding in annotation['boundingPoly']['vertices']:
                b_box.append(bounding['x'])
                b_box.append(bounding['y'])
        except KeyError:
            continue
        word_count += 1
        word_vector = ft.get_word_vector(text)
        final_word = np.append(word_vector, b_box)
        if word_count > word_in_invoice:
            break
        file_data.append(final_word)

    length = len(file_data)
    if length == 0:
        return None
    while length < word_in_invoice:
        difference = word_in_invoice - length
        count = min(difference, length)
        file_data = file_data + file_data[:count]
        length = len(file_data)
    return file_data


@app.route('/cluster', methods=["POST"])
def cluster():
    req = request.get_json()
    # input_json = req['expense_json']
    response = numpy_data(req)
    response = convert_to_dict(response)
    return response


def numpy_datum(candidate):
    up_encoding = np.zeros((310))
    down_encoding = np.zeros((310))
    right_encoding = np.zeros((310))
    left_encoding = np.zeros((310))
    self_encoding = np.zeros((310))

    up_encoding[0:300] = ft.get_word_vector(candidate['neighbours']['up']['description'])
    up_encoding[300] = candidate['neighbours']['up']['boundingPoly']['vertices'][0]['x']
    up_encoding[301] = candidate['neighbours']['up']['boundingPoly']['vertices'][0]['y']
    up_encoding[302] = candidate['neighbours']['up']['boundingPoly']['vertices'][1]['x']
    up_encoding[303] = candidate['neighbours']['up']['boundingPoly']['vertices'][1]['y']
    up_encoding[304] = candidate['neighbours']['up']['boundingPoly']['vertices'][2]['x']
    up_encoding[305] = candidate['neighbours']['up']['boundingPoly']['vertices'][2]['y']
    up_encoding[306] = candidate['neighbours']['up']['boundingPoly']['vertices'][3]['x']
    up_encoding[307] = candidate['neighbours']['up']['boundingPoly']['vertices'][3]['y']
    up_encoding[308] = candidate['neighbours']['up']['distance']
    up_encoding[309] = (candidate['neighbours']['up']['angle'] + 180) / 360

    down_encoding[0:300] = ft.get_word_vector(candidate['neighbours']['down']['description'])
    down_encoding[300] = candidate['neighbours']['down']['boundingPoly']['vertices'][0]['x']
    down_encoding[301] = candidate['neighbours']['down']['boundingPoly']['vertices'][0]['y']
    down_encoding[302] = candidate['neighbours']['down']['boundingPoly']['vertices'][1]['x']
    down_encoding[303] = candidate['neighbours']['down']['boundingPoly']['vertices'][1]['y']
    down_encoding[304] = candidate['neighbours']['down']['boundingPoly']['vertices'][2]['x']
    down_encoding[305] = candidate['neighbours']['down']['boundingPoly']['vertices'][2]['y']
    down_encoding[306] = candidate['neighbours']['down']['boundingPoly']['vertices'][3]['x']
    down_encoding[307] = candidate['neighbours']['down']['boundingPoly']['vertices'][3]['y']
    down_encoding[308] = candidate['neighbours']['down']['distance']
    down_encoding[309] = (candidate['neighbours']['down']['angle'] + 180) / 360

    right_encoding[0:300] = ft.get_word_vector(candidate['neighbours']['right']['description'])
    right_encoding[300] = candidate['neighbours']['right']['boundingPoly']['vertices'][0]['x']
    right_encoding[301] = candidate['neighbours']['right']['boundingPoly']['vertices'][0]['y']
    right_encoding[302] = candidate['neighbours']['right']['boundingPoly']['vertices'][1]['x']
    right_encoding[303] = candidate['neighbours']['right']['boundingPoly']['vertices'][1]['y']
    right_encoding[304] = candidate['neighbours']['right']['boundingPoly']['vertices'][2]['x']
    right_encoding[305] = candidate['neighbours']['right']['boundingPoly']['vertices'][2]['y']
    right_encoding[306] = candidate['neighbours']['right']['boundingPoly']['vertices'][3]['x']
    right_encoding[307] = candidate['neighbours']['right']['boundingPoly']['vertices'][3]['y']
    right_encoding[308] = candidate['neighbours']['right']['distance']
    right_encoding[309] = (candidate['neighbours']['right']['angle'] + 180) / 360

    left_encoding[0:300] = ft.get_word_vector(candidate['neighbours']['left']['description'])
    left_encoding[300] = candidate['neighbours']['left']['boundingPoly']['vertices'][0]['x']
    left_encoding[301] = candidate['neighbours']['left']['boundingPoly']['vertices'][0]['y']
    left_encoding[302] = candidate['neighbours']['left']['boundingPoly']['vertices'][1]['x']
    left_encoding[303] = candidate['neighbours']['left']['boundingPoly']['vertices'][1]['y']
    left_encoding[304] = candidate['neighbours']['left']['boundingPoly']['vertices'][2]['x']
    left_encoding[305] = candidate['neighbours']['left']['boundingPoly']['vertices'][2]['y']
    left_encoding[306] = candidate['neighbours']['left']['boundingPoly']['vertices'][3]['x']
    left_encoding[307] = candidate['neighbours']['left']['boundingPoly']['vertices'][3]['y']
    left_encoding[308] = candidate['neighbours']['left']['distance']
    left_encoding[309] = (candidate['neighbours']['left']['angle'] + 180) / 360

    self_encoding[300] = candidate['annotation']['boundingPoly']['vertices'][0]['x']
    self_encoding[301] = candidate['annotation']['boundingPoly']['vertices'][0]['y']
    self_encoding[302] = candidate['annotation']['boundingPoly']['vertices'][1]['x']
    self_encoding[303] = candidate['annotation']['boundingPoly']['vertices'][1]['y']
    self_encoding[304] = candidate['annotation']['boundingPoly']['vertices'][2]['x']
    self_encoding[305] = candidate['annotation']['boundingPoly']['vertices'][2]['y']
    self_encoding[306] = candidate['annotation']['boundingPoly']['vertices'][3]['x']
    self_encoding[307] = candidate['annotation']['boundingPoly']['vertices'][3]['y']

    datum_encoding = np.zeros((5, 310))
    datum_encoding[0, :] = self_encoding
    datum_encoding[1, :] = up_encoding
    datum_encoding[2, :] = down_encoding
    datum_encoding[3, :] = right_encoding
    datum_encoding[4, :] = left_encoding

    return datum_encoding


def numpy_data_payment_type(candidates):
    numpy_candidates = []
    for candidate in candidates:
        candidate_vector = numpy_datum(candidate)
        numpy_candidates.append(candidate_vector)
    return np.asarray(numpy_candidates)


@app.route('/payment_type', methods=["POST"])
def payment_type():
    req = request.get_json()
    candidates = find_candidates(req)
    np_candidates = numpy_data_payment_type(candidates)
    response = convert_to_dict_payment_type(np_candidates)
    return response
    # try:
        # candidates = find_candidates(req)
        # np_candidates = numpy_data_payment_type(candidates)
        # response = convert_to_dict(np_candidates)
        # a = {'response': 'a'}
        # return a
    # except:
    #     return 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
