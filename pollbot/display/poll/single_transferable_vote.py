from pollbot.models import Vote, User
from sqlalchemy import func
from collections import Counter

def get_stv_result(session, poll):
    users = session.query(User) \
        .join(User.votes) \
        .filter(Vote.poll_id == poll.id) \
        .all()

    print(get_ranked_options(session, poll, poll.options, users))
    return ['Tap "vote" to rank the options by preference']

def get_ranked_options(session, poll, options, users):
    option_ids = [option.id for option in options]
    option_votes = Counter()
    for user in users:
        for vote in sorted(user.votes, key=lambda vote: vote.priority):
            if vote.poll_option_id in option_ids:
                option_votes[vote.poll_option_id] += 1
                break

    return option_votes.most_common()
