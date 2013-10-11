from unittest import TestCase

from hactar import extractor


class TestExtractor(TestCase):
    def get_docs(name):
        with open('test/files/%s.html' % name) as file1:
            html = file1.read()
        with open('test/files/%s.txt' % name) as file2:
            text = file2.read()
        return html, text

    
    def test_epigrams(self):
        html, text = self.get_docs('epigrams')
        out = extractor.extract_text(html)
        self.assertEqual(out, text)


