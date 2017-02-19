#!/usr/bin/env python

import scrapy

from scrapy.crawler import CrawlerProcess

def get_question_pages(questions, answers=None):
    # Returns a list of pages, where each page is the Markdown text to render a
    # single question or answer
    #
    # If answers is None, just render a page for each question. Otherwise,
    # render question pages interleaved with answer pages.
    pages = []
    for i, q in enumerate(questions):
        question_number = i + 1
        if question_number >= 9:
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

class QuizScraper(scrapy.Spider):
    """A scraper for fetching the Guardian weekend quiz"""
    name = 'quiz-scraper'
    start_urls = [
        'https://www.theguardian.com/theguardian/series/the-quiz-thomas-eaton'
    ]

    def parse(self, response):
        # Parses the start URL, which is the index page for the quiz. It finds the
        # first quiz link (i.e. the link to the latest quiz) and passes it to
        # parse_quiz
        quiz_containers = response.css('section.fc-container')
        latest_quiz_url = quiz_containers[0].css('div.fc-item__container a ::attr(href)').extract_first()
        if latest_quiz_url:
            yield scrapy.Request(latest_quiz_url, callback=self.parse_quiz)

    def parse_quiz(self, response):
        # Takes the content of a single quiz page and parses it
        quiz_content = response.css('div.content__article-body p::text').extract()
        quiz_content = [q.strip() for q in quiz_content]

        # quiz_content should now contains 30 lines: the 15 questions and the 15
        # answers
        assert(len(quiz_content) == 30)
        questions = quiz_content[0:15]
        answers = quiz_content[15:30]

        # Get a set of pages for each question...
        pages = get_question_pages(questions)

        # And add a set of pages that repeat the questions and then show the
        # answer on the next page.
        pages.extend(get_question_pages(questions, answers))

        # Now dump the quiz to STDOUT
        print('\n\n---\n\n'.join(pages))

def main():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(QuizScraper)
    process.start()

if __name__ == '__main__':
    main()
