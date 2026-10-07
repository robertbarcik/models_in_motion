from cleaner.string_utils import clean_string

def test_clean_string_strips_whitespace():
    assert clean_string("  hello  ") == "hello"

def test_clean_string_converts_to_lowercase():
    assert clean_string("Hello World") == "hello world"

def test_clean_string_removes_special_characters():
    assert clean_string("hello@world!") == "helloworld"

def test_clean_string_combined():
    assert clean_string("  Hello, World! ") == "hello world"
