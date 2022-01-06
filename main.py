from collections import Counter
import json

from Levenshtein import distance


def levenshtein(a, b):
    if len(a) == 0:
        return len(b)
    if len(b) == 0:
        return len(a)
    if a[0] == b[0]:
        return levenshtein(a[1:], b[1:])
    return 1 + min(levenshtein(a[1:], b),
                   levenshtein(a, b[1:]),
                   levenshtein(a[1:], b[1:]))


def get_single_letter_count(words):
    letter_count = Counter("".join(set(x for x in words)))
    return letter_count


def get_word_key_dict(words):
    word_key_dict = {}
    for x in words:
        key = tuple(sorted(x))
        if key not in word_key_dict:
            word_key_dict[key] = [1, 0, 0, 0, 0, 0]
        else:
            word_key_dict[key][0] += 1
    return word_key_dict


def find_most_common_set(word_key_dict):
    best_count = 0
    best_key = None
    for key in word_key_dict:
        if best_count < word_key_dict[key][0]:
            best_count = word_key_dict[key][0]
            best_key = key

    return best_key, best_count


def letter_match_comparisons(word_key_dict):
    keys = list(word_key_dict.keys())

    # Get distances for all letter sets
    for i in range(len(keys)):
        if i % 100 == 0:
            print(i, len(keys))
        for k in range(i+1, len(keys)):
            dist = distance(keys[i], keys[k])
            word_key_dict[keys[i]][dist] += 1
            word_key_dict[keys[k]][dist] += 1

    return word_key_dict


def main():
    # Get each word (ignore newline at end)
    words = [x[:-1] for x in open("data/wordle.txt", 'r')]

    print("================================")
    print("Single Letter Count")
    print("================================")
    letter_count = get_single_letter_count(words)
    for letter in letter_count:
        print(letter, ":", "%2.1f" % (letter_count[letter] / len(words) * 100) + "%")

    print()
    print("================================")
    print("Best Letter Set")
    print("================================")
    word_key_dict = get_word_key_dict(words)
    key, count = find_most_common_set(word_key_dict)
    print(key, ':', count, '=', "%2.4f" % (count / len(words)) + '%')

    word_key_dict = letter_match_comparisons(word_key_dict)

    word_dict = {x: word_key_dict[tuple(sorted(x))] for x in words}
    json.dump(word_dict, open("data/word_frequency.txt", "w"))


if __name__ == "__main__":
    main()
