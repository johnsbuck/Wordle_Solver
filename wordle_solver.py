import sqlite3 as sql
import re
import json
import math

from Levenshtein import distance


def get_word_key_dict(words):
    word_key_dict = {}
    for x in words:
        key = tuple(sorted(x))
        if key not in word_key_dict:
            word_key_dict[key] = [1, 0, 0, 0, 0, 0]
        else:
            word_key_dict[key][0] += 1
    return word_key_dict


def letter_match_comparisons(word_key_dict):
    keys = list(word_key_dict.keys())

    # Get distances for all letter sets
    for i in range(len(keys)):
        if i % 100 == 0:
            print(i, len(keys))
        for k in range(i+1, len(keys)):
            dist = distance(keys[i], keys[k])
            word_key_dict[keys[i]][dist] += word_key_dict[keys[k]][0]
            word_key_dict[keys[k]][dist] += word_key_dict[keys[i]][0]

    return word_key_dict


def generate_word_frequency(words, filename="data/word_frequency.json"):
    word_key_dict = get_word_key_dict(words)
    word_key_dict = letter_match_comparisons(word_key_dict)
    word_dict = {x: word_key_dict[tuple(sorted(x))] for x in words}
    if filename is not None:
        json.dump(word_dict, open(filename, "w"))
    return word_dict


def find_next_word(word_frequency, std=False):
    mean = 1 / 6.
    best = None
    best_word = None
    for key in word_frequency:
        frequency = [x / len(word_frequency.keys()) for x in word_frequency[key]]

        if not std:
            idx = -1
            while frequency[idx] == 0:
                idx -= 1
            curr = (idx, frequency[idx])
        else:
            curr = math.sqrt(sum(math.pow(x - mean, 2) for x in frequency) / len(frequency))
        if std and (best is None or curr < best):
            best = curr
            best_word = key
        elif best is None or curr[0] < best[0] or (curr[0] == best[0] and curr[1] < best[1]):
            best = curr
            best_word = key
    print(best_word, best)
    print([x / len(word_frequency.keys()) for x in word_frequency[best_word]])
    print()
    return best_word


def get_wordle_result(word, ban_letters, ban_areas, found_letters, search_letters):
    # Prompt
    print("What was the result of " + word + "?")
    print("0=Grey")
    print("1=Yellow")
    print("2=Green")
    print("Word:", word)

    # Get outcome of word
    outcome = input(" Ans: ")
    while len(outcome) != 5 or re.fullmatch('^[0|1|2]*$', outcome) is None:
        print()
        print("Invalid Input")
        print("Word:", word)
        outcome = input(" Ans: ")
    print()

    # Parse results of outcome
    new_search = {}
    for i in range(len(word)):
        if outcome[i] == '0':
            if word[i] in new_search:
                ban_areas[i] += word[i]
            else:
                ban_letters.append(word[i])     # Letters that are removed from play
        elif outcome[i] == '1':
            ban_areas[i] += word[i]         # Letters that aren't removed from play, but are not in specified area
            if word[i] not in new_search:
                new_search[word[i]] = 1
            else:
                new_search[word[i]] += 1
        elif found_letters[i] == '':
            found_letters[i] = word[i]   # Found letters and positions
            if word[i] in search_letters:
                search_letters[word[i]] -= 1
                if search_letters[word[i]] == 0:
                    del search_letters[word[i]]

    for key in new_search:
        if key not in search_letters or new_search[key] > search_letters[key]:
            search_letters[key] = new_search[key]

    return outcome


def get_regex_expr(ban_letters, ban_areas, found_letters, search_letters):
    ban_expr = ""
    for i in range(5):
        curr = found_letters[i]
        if found_letters[i] == '':
            curr = "[^" + "".join(ban_letters) + ban_areas[i] + "]"
        ban_expr += curr

    search_expr = ""
    for key in search_letters:
        curr = "([^" + key + "])*"
        curr = "^(" + curr + key + curr + "){" + str(search_letters[key]) + ",}$"
        search_expr += "(?=" + curr + ")"

    return "(?=" + ban_expr + ")" + search_expr


# https://stackoverflow.com/questions/5365451/problem-with-regexp-python-and-sqlite
def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None


def main():
    # ================================
    # Connect to Database
    # ================================
    con = sql.connect("data/test.db")
    con.create_function("REGEXP", 2, regexp)

    cur = con.cursor()

    # Check if table exists, if not make new table
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    if len(cur.fetchall()) == 0:
        cur.execute("CREATE TABLE words (word text unique not null);")

        with open("data/wordle.txt", 'r') as f:
            for line in f:
                cur.execute("INSERT INTO words VALUES (?)", [line[:-1]])

    # ================================
    # Initial Word Search
    # (Not used since the result is always "erase")
    # ================================
    # cur.execute("SELECT word FROM words;")
    # words = [x[0] for x in cur.fetchall()]
    # word_frequency = generate_word_frequency(words, None)
    # new_word = find_next_word(word_frequency)

    # ================================
    # Set Initial Parameters
    # ================================
    std = False
    ban_letters = []    # List of letters that are out of game
    ban_areas = ['' for _ in range(5)]  # Letters that are not out of game, but not in the specified position
    found_letters = ['' for _ in range(5)]  # Found letters for the given position
    search_letters = {}     # Letters being searched and their count
    if std:
        curr_word = "arise"     # Using "arise" based on initial search with standard deviation
    else:
        curr_word = "stoae"     # Using "stoae" based on initial search with other method
    outcome = None  # Outcome of each word

    # Select random word (if you want to try without using the site)
    cur.execute("SELECT word FROM words ORDER BY random() LIMIT 1;")
    print("Optional Play Word:", cur.fetchall()[0][0])

    # ================================
    # Play Wordle
    # ================================
    for _ in range(6):
        # Get outcome of current guess
        outcome = get_wordle_result(curr_word, ban_letters, ban_areas, found_letters, search_letters)

        # If guess is successful, end game
        if outcome == '22222':
            print("SUCCESS!")
            break

        # Get Regex Expression from gathered information
        expr = get_regex_expr(ban_letters, ban_areas, found_letters, search_letters)
        print("Regex Expression:", expr)

        # Execute Query on Words
        cur.execute("SELECT word FROM words WHERE word REGEXP ?", [expr])
        words = [x[0] for x in cur.fetchall()]
        print("# of Words Remaining:", len(words))

        if len(words) == 0:
            print("There are no more words available!")
            break

        # Generate Word Frequency Dictionary
        word_frequency = generate_word_frequency(words, None)

        # Find next word based on standard deviation and word frequency
        curr_word = find_next_word(word_frequency, std=std)

    # ================================
    # End of Wordle Game
    # ================================

    # If word not found
    if outcome != "22222":
        print("FAILURE!")

    # End connection with database
    con.commit()
    con.close()


if __name__ == "__main__":
    main()
