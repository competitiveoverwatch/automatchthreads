from config import data as config
import praw

reddit = praw.Reddit(client_id = config['creds']['redditBotClientId'], client_secret = config['creds']['redditBotClientSecret'], password = config['creds']['redditBotPassword'], username = config['creds']['redditBotUserName'], user_agent=config['config']['reddit_user_agent'])
subreddit = reddit.subreddit(config['config']['subreddit'])

class Reddit():
    @classmethod
    def new_thread(cls, thread_title, thread_body):
        """Create a new reddit thread."""
        submission = subreddit.submit(title=thread_title, selftext=thread_body, send_replies=False)
        return submission.shortlink
        
    @classmethod
    def edit_thread(cls, thread_link, thread_body):
        """Edit an existing reddit thread given via a link."""
        submission = reddit.submission(url=thread_link)
        submission.edit(thread_body)
        
    @classmethod
    def setup_thread(cls, thread_link, sticky=False, sort_new=False, spoiler=True):
        """Set up an existing reddit thread."""
        submission = reddit.submission(url=thread_link)
        if sticky:
            submission.mod.sticky(state=True, bottom=True)
        if spoiler:
            submission.mod.spoiler()
        if sort_new:
            submission.mod.suggested_sort(sort='new')
        cls.flair_thread(thread_link)
        
    @classmethod
    def flair_thread(cls, thread_link, live=False):
        """Flair a reddit thread as Match Thread, optionally give it the LIVE text."""
        submission = reddit.submission(url=thread_link)
        if live and submission.link_flair_text != 'LIVE':
            submission.mod.flair(text='LIVE', css_class='Match')
        else:
            if submission.link_flair_text != 'Match Thread':
                submission.mod.flair(text='Match Thread', css_class='Match')
                
        
    @classmethod
    def getComments(cls, threadLink):
        submission = reddit.submission(url=threadLink)
        submission.comments.replace_more()
        return submission.comments
        
    @classmethod
    def getNewPosts(cls):
        return subreddit.new(limit=100)