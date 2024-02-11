import argparse
import re
from urllib import request, error


class ParameterException(Exception):
    pass


class RequestException(Exception):
    pass


def get_page_content(url):
    try:
        with request.urlopen(url) as f:
            status = f.status
            if status != 200:
                raise RequestException(f'Server return status {status} instead of 200')
            else:
                content = f.read().decode('utf-8')
                with open('cp.txt', mode='w+') as my_file:
                    my_file.write(repr(content))
                return content
    except error.URLError:
        raise RequestException(f'Connection with {url} can not be established')


def clear_page_content(page_content):
    remove_multilinescript_pattern = re.compile('<(script|style)(.|\n)*?>(.|\n)*?</(script|style)>')
    remove_symbols_pattern = re.compile('(&#\d*;)')
    pattern = re.compile('<.*?>', flags=(re.MULTILINE | re.DOTALL))
    scripts_removed = re.sub(remove_multilinescript_pattern, '', page_content)
    symbols_removed = re.sub(remove_symbols_pattern, '', scripts_removed)
    result = re.sub(pattern, '', symbols_removed)
    return result


def remove_all_punctuation_marks(human_readable_content):
    remove_punctuation_marks_pattern = re.compile('[^a-zA-Z0-9 \n]')
    marks_removed = re.sub(remove_punctuation_marks_pattern, '', human_readable_content)
    return marks_removed


def divide_text_to_individual_words(text):
    return text.split()


def calculate_words_occurrences(words):
    words_occurrences = {}
    for word in words:
        words_occurrences.setdefault(word.lower(), 0)
        words_occurrences[word.lower()] += 1
    return words_occurrences


def sort_words_occurrences(occurrences):
    return sorted(occurrences.items(), key=lambda item: item[1], reverse=True)


def print_top_ten(sorted_occurrences):
    for item in sorted_occurrences[:10]:
        print(f'{item[0]}: {item[1]}')


def save_results(sorted_occurrences):
    with open('results.txt', mode='w+') as my_file:
        for item in sorted_occurrences:
            my_file.write(f'{item[0]}: {item[1]}\n')


def parse_input():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str)
    args = parser.parse_args()
    parameter = args.url

    if not args.url:
        raise ParameterException("URL not provided")
    if not isinstance(parameter, str):
        raise ParameterException("URL {}} is not a string".format(parameter))
    if len(parameter) > 2048:
        raise ParameterException(f'URL exceeds its maximum length of 2048 characters (given length={len(parameter)}')

    regex = re.compile(
        r'^(?:http)s?://'  # http:// or https://
        r'(?:(?:[A-Z\d](?:[A-Z\d-]{0,61}[A-Z\d])?\.)+(?:[A-Z]{2,6}\.?|[A-Z\d-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if not re.match(regex, parameter):
        raise ParameterException("URL is not valid (given url={})".format(parameter))
    else:
        return parameter


def main():
    try:
        url = parse_input()
        page_content = get_page_content(url)
        human_readable_content = clear_page_content(page_content)
        text_without_punctuation_marks = remove_all_punctuation_marks(human_readable_content)
        words = divide_text_to_individual_words(text_without_punctuation_marks)
        words_occurrences = calculate_words_occurrences(words)
        sorted_occurrences = sort_words_occurrences(words_occurrences)
        print_top_ten(sorted_occurrences)
        save_results(sorted_occurrences)
    except (ParameterException, RequestException) as e:
        print(e.args[0])
        raise SystemExit(1)


if __name__ == '__main__':
    main()
