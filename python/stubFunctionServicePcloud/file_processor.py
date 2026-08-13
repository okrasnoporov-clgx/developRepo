def count_words(content: str) -> int:
    return len(content.split())


def create_stat_line(filename: str, content: str) -> str:
    word_count = count_words(content)
    return f"{filename} - {word_count}\n"
