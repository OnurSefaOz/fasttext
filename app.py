import fasttext
import json
import numpy as np
from flask import Flask, request


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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
