import scrapy

from scrapy.crawler import CrawlerProcess

def get_question_pages(questions, answers=None):
    pages = []
    for i, q in enumerate(questions):
        if i >= 8:
            page = '# {}: what links?\n\n'.format(i + 1)
            q = q.rstrip('?')
            page = page + '\n'.join(['- {}'.format(opt) for opt in q.split('; ')])
            pages.append(page)
        else:
            pages.append('# {}\n\n{}'.format(i + 1, q))

        if answers:
            pages.append(answers[i])
    return pages

class QuizScraper(scrapy.Spider):
    """A scraper for fetching the Guardian weekend quiz"""
    name = 'quiz-scraper'
    start_urls = [
        'https://www.theguardian.com/theguardian/series/the-quiz-thomas-eaton'
    ]

    def parse(self, response):
        quiz_containers = response.css('section.fc-container')
        latest_quiz_url = quiz_containers[0].css('div.fc-item__container a ::attr(href)').extract_first()
        if latest_quiz_url:
            yield scrapy.Request(latest_quiz_url, callback=self.parse_quiz)

    def parse_quiz(self, response):
        quiz = response.css('div.content__article-body p::text').extract()
        quiz = [q.strip() for q in quiz]
        assert(len(quiz) == 30)

        questions = quiz[0:15]
        answers = quiz[15:30]

        pages = get_question_pages(questions)
        pages.extend(get_question_pages(questions, answers))
        print('\n\n---\n\n'.join(pages))

def main():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(QuizScraper)
    process.start()

if __name__ == '__main__':
    main()
