import pytest
from main import clean_and_convert_html

def test_heading_conversion():
    html = "<h2>Subtitle 1</h2><p>Text</p><h3>Subtitle 2</h3>"
    result = clean_and_convert_html(html)
    assert "## Subtitle 1" in result
    assert "### Subtitle 2" in result

def test_relative_links_preservation():
    html = '<a href="[https://support.optisigns.com/hc/en-us/articles/123](https://support.optisigns.com/hc/en-us/articles/123)">Click here</a>'
    result = clean_and_convert_html(html, domain="[https://support.optisigns.com](https://support.optisigns.com)")
    assert "[Click here](/hc/en-us/articles/123)" in result
    assert "[https://support.optisigns.com](https://support.optisigns.com)" not in result

def test_code_block_preservation():
    html = "<pre><code>const a = 10;\nconsole.log(a);</code></pre>"
    result = clean_and_convert_html(html)
    assert "```" in result
    assert "console.log(a);" in result

def test_strip_unwanted_tags():
    html = "<script>alert('hack')</script><style>.css{}</style><p>Valid content</p>"
    result = clean_and_convert_html(html)
    assert "alert" not in result
    assert ".css" not in result
    assert "Valid content" in result

def test_empty_input():
    assert clean_and_convert_html("") == ""
    assert clean_and_convert_html(None) == ""