import scrapy

from scrapy.crawler import CrawlerProcess

def print_questions(questions, answers=None):
    for i, q in enumerate(questions):
        if i >= 8:
            print('# {}: what links?\n\n'.format(i + 1))
            q = q.rstrip('?')
            q = '\n'.join(['- {}'.format(opt) for opt in q.split('; ')])
        else:
            print('# {}\n'.format(i + 1))

        print('{}\n\n---\n'.format(q))

        if answers:
            answer = answers[i]
            print('{}\n\n---\n'.format(answer))

class QuizScraper(scrapy.Spider):
    """A scraper for fetching the Guardian weekend quiz"""
    name = 'quiz-scraper'
    start_urls = [
        'https://www.theguardian.com/theguardian/series/the-quiz-thomas-eaton'
    ]

    def parse(self, response):
        quiz_containers = response.css('section.fc-container')
        href = quiz_containers[0].css('div.fc-item__container a ::attr(href)').extract_first()
        if href:
            yield scrapy.Request(href, callback=self.parse_quiz)

    def parse_quiz(self, response):
        quiz = response.css('div.content__article-body p::text').extract()
        quiz = [q.strip() for q in quiz]
        if quiz:
            assert(len(quiz) == 30)
            questions = quiz[0:15]
            answers = quiz[15:30]

            print_questions(questions)
            print_questions(questions, answers)

def main():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(QuizScraper)
    process.start()

if __name__ == '__main__':
    main()
