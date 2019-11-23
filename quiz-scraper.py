#!/usr/bin/env python

import re
import scrapy

from scrapy.crawler import CrawlerProcess

# The quiz is split into regular questions and "what links" questions. Regular
# questions come first.
NUM_REGULAR_QUESTIONS = 8
TOTAL_QUESTIONS = 15

def get_question_pages(questions, answers=None):
    """
    Returns a list of pages, where each page is the Markdown text to render a
    single question or answer

    If answers is None, just render a page for each question. Otherwise,
    render question pages interleaved with answer pages.
    """
    pages = []
    for i, q in enumerate(questions):
        question_number = i + 1
        if question_number > NUM_REGULAR_QUESTIONS:
            # Questions 9 onwards are "what links" questions
            page = '# {}: What links?\n\n'.format(question_number)

            # Remove trailing question marks from the question
            q = q.rstrip('?')

            # Split the question on semicolons, turn into bulleted list
            page += '\n'.join(['- {}'.format(opt) for opt in q.split('; ')])
            pages.append(page)
        else:
            pages.append('# {}\n\n{}'.format(question_number, q))

        if answers:
            # If answers were provided, interleave answer pages with question
            # pages
            pages.append(answers[i])
    return pages

def get_summary_pages(answers):
    pages = []
    page = ''
    for i, a in enumerate(answers):
        page += '- {}\n'.format(a)
        if i % 5 == 4:
            pages.append(page)
            page = ''
    return pages

def strip_leading_ordinals(strings_list):
    """
    Removes leading ordinals that may appear as a result of dodgy formatting
    on the source website.
    """
    results = []
    for (i, string) in enumerate(strings_list):
        ordinal = i + 1
        regex = re.compile('^{}\s+'.format(ordinal))
        results.append(re.sub(regex, '', string))
    return results

class QuizScraper(scrapy.Spider):
    """A scraper for fetching the Guardian weekend quiz"""
    name = 'quiz-scraper'
    start_urls = [
        'https://www.theguardian.com/theguardian/series/the-quiz-thomas-eaton'
    ]

    def parse(self, response):
        # Parses the start URL, which is the index page for the quiz. It finds
        # the first quiz link (i.e. the link to the latest quiz) and passes it
        # to parse_quiz
        quiz_containers = response.css('section.fc-container')
        latest_quiz_url = quiz_containers[0].css('div.fc-item__container a ::attr(href)').extract_first()
        if latest_quiz_url:
            yield scrapy.Request(latest_quiz_url, callback=self.parse_quiz)

    def parse_quiz(self, response):
        # Takes the content of a single quiz page and parses it
        quiz_content = response.css('div.content__article-body p::text').extract()
        quiz_content = [q.strip() for q in quiz_content if len(q.strip()) > 0]

        total_elements = TOTAL_QUESTIONS * 2

        # Get rid of the ad for Eaton's new book
        if len(quiz_content) == total_elements + 2 and quiz_content[total_elements].startswith('Eaton'):
            quiz_content = quiz_content[:total_elements]

        # quiz_content should now contains `total_elements` lines: the
        # `TOTAL_QUESTIONS` questions and the same number of answers
        assert len(quiz_content) == total_elements, ('expected %d elements, got %d' % (total_elements, len(quiz_content)))
        questions = strip_leading_ordinals(quiz_content[0:TOTAL_QUESTIONS])
        answers = strip_leading_ordinals(quiz_content[TOTAL_QUESTIONS:TOTAL_QUESTIONS*2])

        # Get a set of pages for each question...
        pages = get_question_pages(questions)

        # And add a set of pages that repeat the questions and then show the
        # answer on the next page.
        pages.extend(get_question_pages(questions, answers))

        pages.extend(get_summary_pages(answers))

        # Now dump the quiz to STDOUT
        print(('\n\n---\n\n'.join(pages)))

def main():
    process = CrawlerProcess({
        'LOG_LEVEL': 'WARN',
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(QuizScraper)
    process.start()

if __name__ == '__main__':
    main()
