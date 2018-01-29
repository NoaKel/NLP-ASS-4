import json
import string
import numpy as np

countriesCities = json.load(open('countries.json'))

countries = set([c.lower() for c in countriesCities.keys()])
countries.add("u.s")
for country in set(countries):
    countries.add(string.replace(country, ' ', '-'))

cities = set(reduce(lambda a, b: a + [c.lower() for c in b], countriesCities.values(), []))

for city in set(cities):
    cities.add(string.replace(city, ' ', '-'))

SHIFT = 1
START = "START"
END = "END"

UP = "UP"
DOWN = "DOWN"
TOP = "TOP"


def readVectorsFromFile(fileName):
    words = {}
    print "Reading", fileName
    with open(fileName, "r") as lines:
        for line in lines:
            vector = line.split()
            word = vector.pop(0)
            words[word] = map(float, vector)
    # maxWordLen = max(maxWordLen, len(word)) # This returns like 50
    return words


word2vec = {}  # readVectorsFromFile("deps.words")
unknownVector = list(np.zeros(300))


def to_string_points_to_the_other(first_chunk, second_chunk, sentence, id):
    first, second = find_dependency_routes(first_chunk, second_chunk, sentence)
    if len(first) == 1:
        # print "1"
        return ["TheFirstPointsToTheSecond%s" % id]
    # print len(first)
    return []


def to_string_previous_tag(chunk, sentence, id):
    return "PreviousTag%s(%s)" % (id, get_previous_tag(chunk, sentence))


def parse_chunk(chunk):  # Fixed
    return chunk["text"]


def to_string_words_in_chunk(chunk):
    return "WordsInChunk(%s)" % parse_chunk(chunk)


def to_string_word_before_chunk(id, chunk, sentence):
    return "WordBeforeChunk%s(%s)" % (id, get_previous_word(chunk, sentence))


def to_string_word_after_chunk(id, chunk, sentence):
    return "WordAfterChunk%s(%s)" % (id, get_next_word(chunk, sentence))


def get_previous_tag(chunk, sentence):
    id_first_word_in_chunk = chunk["firstWordIndex"]
    if id_first_word_in_chunk - 1 - SHIFT >= 0:
        return sentence[id_first_word_in_chunk - 1 - SHIFT]['pos']
    return START


def get_previous_word(chunk, sentence):
    id_first_word_in_chunk = chunk["firstWordIndex"]
    if id_first_word_in_chunk - 1 - SHIFT >= 0:
        return sentence[id_first_word_in_chunk - 1 - SHIFT]['word']
    return START


def get_next_word(chunk, sentence):
    id_last_word_in_chunk = chunk["lastWordIndex"]
    if id_last_word_in_chunk + 1 - SHIFT < len(sentence):
        return sentence[id_last_word_in_chunk + 1 - SHIFT]['word']
    return START


def to_string_distance_between_chunks(first_chunk, second_chunk, sentence):
    if first_chunk["firstWordIndex"] > second_chunk["firstWordIndex"]:
        return "Distance(%s)" % ((first_chunk["firstWordIndex"] - second_chunk["lastWordIndex"]) < 10)
    return "Distance(%s)" % ((second_chunk["firstWordIndex"] - first_chunk["lastWordIndex"]) < 10)


def type_tag(chunk, id):  # Fixed
    return "Type%s(%s)" % (id, chunk["entType"])


def concat_tag(chunk1, chunk2):  # Fixed
    return "TypeConcat(%s)" % (chunk1["entType"] + chunk2["entType"])


def to_string_find_dependency_tag_list(first_chunk, second_chunk, sentence):
    graph = find_dependency_graph(first_chunk, second_chunk, sentence)
    all_dependency_tags = []
    i = 0
    while graph[i] != graph[i + 1]:
        all_dependency_tags.append(to_string_dependency_tag(UP, graph[i], sentence))
        i += 1
        if i + 1 >= len(graph):
            return all_dependency_tags
    i += 1
    all_dependency_tags.append(to_string_dependency_tag(TOP, graph[i], sentence))
    i += 1
    while i < len(graph):
        all_dependency_tags.append(to_string_dependency_tag(DOWN, graph[i], sentence))
        i += 1
    return all_dependency_tags


def to_string_find_dependency_word_list(first_chunk, second_chunk, sentence):
    graph = find_dependency_graph(first_chunk, second_chunk, sentence)
    all_dependency_tags = []
    i = 0
    while graph[i] != graph[i + 1]:
        all_dependency_tags.append(to_string_dependency_word(UP, graph[i], sentence))
        i += 1
        if i + 1 >= len(graph):
            return all_dependency_tags
    i += 1
    all_dependency_tags.append(to_string_dependency_word(TOP, graph[i], sentence))
    i += 1
    while i < len(graph):
        all_dependency_tags.append(to_string_dependency_word(DOWN, graph[i], sentence))
        i += 1
    return all_dependency_tags


def to_string_find_dependency_type_list(first_chunk, second_chunk, sentence):
    graph = find_dependency_graph(first_chunk, second_chunk, sentence)
    all_dependency_tags = []
    i = 0
    while graph[i] != graph[i + 1]:
        all_dependency_tags.append(to_string_dependency_type(UP, graph[i], sentence))
        i += 1
        if i + 1 >= len(graph):
            return all_dependency_tags
    i += 1
    all_dependency_tags.append(to_string_dependency_type(TOP, graph[i], sentence))
    i += 1
    while i < len(graph):
        all_dependency_tags.append(to_string_dependency_type(DOWN, graph[i], sentence))
        i += 1
    return all_dependency_tags


def to_string_find_dependency_type_list2(first_chunk, second_chunk, sentence):
    graph = find_dependency_graph(first_chunk, second_chunk, sentence)
    all_dependency_tags = []
    i = 0
    # while graph[i] != graph[i + 1]:
    #     all_dependency_tags.append(to_string_dependency_type(UP, graph[i], sentence))
    #     i += 1
    #     if i + 1 >= len(graph):
    #         return all_dependency_tags
    # i += 1
    # all_dependency_tags.append(to_string_dependency_type(TOP, graph[i], sentence))
    # i += 1
    while i < len(graph):
        tag = word_content(i, sentence)['dependency']
        feature = "DependencyType2(%s)" % tag
        all_dependency_tags.append(feature)
        i += 1
    return all_dependency_tags


def to_string_dependency_tag(direction, id, sentence):
    word_context = sentence[id - SHIFT]
    tag = word_context['tag']
    return "DependencyTag%s(%s)" % (1, tag)


def to_string_dependency_type(direction, id, sentence):
    tag = word_content(id, sentence)['dependency']
    return "DependencyType%s(%s)" % (direction, tag)


def word_content(id, sentence):
    return sentence[id - SHIFT]


def to_string_dependency_word(direction, id, sentence):
    word_context = sentence[id - SHIFT]
    tag = word_context['lemma']
    return "DependencyWord%s(%s)" % (1, tag)


def find_dependency_route(chunk, sentence):
    firstWord = sentence[chunk["firstWordIndex"]]
    parent = firstWord['parent']
    current_id = firstWord['id']
    while chunk["firstWordIndex"] <= parent - SHIFT <= chunk["lastWordIndex"]:
        current_id = parent
        parent = sentence[parent - SHIFT]['parent']
    path = [current_id]
    while True:
        path.append(parent)
        if parent == 0:
            break
        parent = sentence[parent - SHIFT]['parent']
    return path


def dispose_overlapping(first_route, second_route):
    overlapping = -1
    while overlapping > -len(first_route) and overlapping > -len(second_route) and first_route[overlapping] == \
            second_route[overlapping]:
        overlapping -= 1
    if overlapping == -1:
        return first_route, second_route
    return first_route[0:overlapping + 1], second_route[0:overlapping + 1]


# TODO: Use this method to get features.
def find_dependency_graph(first_chunk, second_chunk, sentence):
    first, second = find_dependency_routes(first_chunk, second_chunk, sentence)
    return first + list(reversed(second))


def find_dependency_routes(first_chunk, second_chunk, sentence):
    first_route = find_dependency_route(first_chunk, sentence)
    second_route = find_dependency_route(second_chunk, sentence)
    first, second = dispose_overlapping(first_route, second_route)
    return first, second


def to_string_second_previous_tag(chunk, sentence, id):
    return "SecondPreviousTag%s(%s)" % (id, get_second_previous_tag(chunk, sentence))


def get_second_previous_tag(chunk, sentence):
    id_first_word_in_chunk = chunk["firstWordIndex"]
    if id_first_word_in_chunk - 2 - SHIFT >= 0:
        return sentence[id_first_word_in_chunk - 2 - SHIFT]['pos']
    return START


def to_string_forward_tag(chunk, sentence, id):
    return "ForwardTag%s(%s)" % (id, get_forward_tag(chunk, sentence))


def get_forward_tag(chunk, sentence):
    id_first_word_in_chunk = chunk["lastWordIndex"]
    if id_first_word_in_chunk + 1 - SHIFT < len(sentence):
        return sentence[id_first_word_in_chunk + 1 - SHIFT]['pos']
    return END


def to_string_second_forward_tag(chunk, sentence, id):
    return "SecondForwardTag%s(%s)" % (id, get_second_forward_tag(chunk, sentence))


def get_second_forward_tag(chunk, sentence):
    id_first_word_in_chunk = chunk["firstWordIndex"]
    if id_first_word_in_chunk + 2 - SHIFT < len(sentence):
        return sentence[id_first_word_in_chunk + 2 - SHIFT]['pos']
    return END


def to_string_chunk_head(chunk, sentence, id):
    return "HeadTag%s(%s)" % (id, chunk["headWordTag"])


def to_string_chunk_head_dependency(chunk, sentence, id):
    return "HeadDependency%s(%s)" % (id, get_head_dependency(chunk, sentence))


def get_head_tag(chunk, sentence):
    ids = range(chunk["firstWordIndex"], chunk["lastWordIndex"] + 1)
    for word in chunk:
        if word["parent"] not in ids:
            return sentence[word["parent"] - SHIFT]["tag"]


def get_head_dependency(chunk, sentence):
    ids = range(chunk["firstWordIndex"], chunk["lastWordIndex"] + 1)
    for word in chunk:
        if word["parent"] not in ids:
            return sentence[word["parent"] - SHIFT]["dependency"]


def to_string_bag_of_words(first_chunk, second_chunk, sentence):
    first, second = get_first_and_second_chunk(first_chunk, second_chunk)
    between_words = sentence[first["lastWordIndex"]:second["firstWordIndex"] - 1]

    return ["BagOfWords%s" % word["lemma"] for word in between_words]


def get_first_and_second_chunk(first_chunk, second_chunk):
    if first_chunk["firstWordIndex"] < second_chunk["firstWordIndex"]:
        return first_chunk, second_chunk
    return second_chunk, first_chunk


def get_head_id(chunk, sentence):
    ids = set()
    for word in chunk:
        ids.add(word["id"])
    for word in chunk:
        if word["parent"] not in ids:
            return word["id"]


def has_numbers(chunk, id):
    return "HasNumbers%s(%s)" % (id, "T" if any([c.isdigit() for c in chunk["text"]]) else "F")


def is_chunk_uppercase(chunk, id):
    return "ChunkUppercase%s(%s)" % (id, "T" if chunk["text"][0].isupper() else "F")


def is_city(chunk):
    return "City(%s)" % ("T" if chunk["text"] in cities else "F")


def is_country(chunk):
    return "Country(%s)" % ("T" if chunk["text"] in countries else "F")


def is_location(chunk, id):
    text = chunk["text"].lower()
    return "IsLocation%s(%s)" % (id, "T" if text in countries or text in cities else "F")


def get_word_vector(word):
    word = word.lower()
    if word in word2vec:
        return word2vec[word]
    return unknownVector


def sum_vectors(vectors):
    return [sum(x) for x in zip(*vectors)]


def chunk_to_vector(chunk):
    return sum_vectors([get_word_vector(word) for word in chunk["text"].split()])


def prev_word_vector(chunk, sentence):
    return get_word_vector(get_previous_word(chunk, sentence))


def next_word_vector(chunk, sentence):
    return get_word_vector(get_next_word(chunk, sentence))


def head_word_vector(chunk):
    return get_word_vector(chunk["rootHead"])


def sentence_vector(sentence):
    return sum_vectors([get_word_vector(word) for word in [word["word"] for word in sentence]])


class FeaturesBuilder:
    def __init__(self):
        pass

    def build_features(self, first_chunk, second_chunk, sentence):
        # print first_chunk
        # print second_chunk
        # print sentence
        return [type_tag(first_chunk, 1),
                type_tag(second_chunk, 2),
                to_string_words_in_chunk(first_chunk),
                to_string_words_in_chunk(second_chunk),
                concat_tag(first_chunk, second_chunk),
                # is_chunk_uppercase(first_chunk, 1),
                # is_chunk_uppercase(second_chunk, 2),
                # is_country(second_chunk),
                # is_city(second_chunk),
                is_location(first_chunk, 1),
                is_location(second_chunk, 2),
                # has_numbers(first_chunk, 1),
                # has_numbers(second_chunk, 2),
                to_string_word_before_chunk(1, first_chunk, sentence),
                to_string_word_after_chunk(2, second_chunk, sentence),
                to_string_forward_tag(first_chunk, sentence, 1),
                to_string_chunk_head(first_chunk, sentence, 1),
                to_string_chunk_head(second_chunk, sentence, 2)] \
               + to_string_bag_of_words(first_chunk, second_chunk, sentence) \
        + to_string_find_dependency_tag_list(first_chunk, second_chunk, sentence) \
        + to_string_find_dependency_word_list(first_chunk, second_chunk, sentence) \
        + to_string_find_dependency_type_list(first_chunk, second_chunk, sentence)

    def build_vector(self, first_chunk, second_chunk, sentence):
        return []
        # + chunk_to_vector(first_chunk) \
        # + chunk_to_vector(second_chunk)
        # + head_word_vector(first_chunk) \
        # + head_word_vector(second_chunk) \
        # + prev_word_vector(first_chunk, sentence) \
        # + next_word_vector(first_chunk, sentence) \
        # + prev_word_vector(second_chunk, sentence) \
        # + next_word_vector(second_chunk, sentence)
    # + sentence_vector(sentence)


class FeatureBuilders:
    ALL = [FeaturesBuilder()]
