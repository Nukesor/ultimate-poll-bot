from pollbot.models import Vote, User, PollOption
from sqlalchemy import func
from collections import Counter

def get_stv_result(session, poll):
    users = session.query(User) \
        .join(User.votes) \
        .filter(Vote.poll_id == poll.id) \
        .all()

    option_ids = [option.id for option in poll.options]
    print('init ids',option_ids)
    for _ in range(len(option_ids) - 1):
        ranked_options = get_ranked_options(session, poll, option_ids, users)
        print('ranked', ranked_options)
        last_id, last_rank = ranked_options[-1]
        options_with_same_rank = [
            id for id, rank in ranked_options
            if rank == last_rank and id != last_id
        ]

        if (len(options_with_same_rank) > 0):
            names = ','.join([
                session.query(PollOption).get(id).name
                for id in options_with_same_rank + [last_id]
            ])
            return [f'There was a tie between {names}. Close the poll to resolve it using a random choice.']

        option_ids = [
            id for id in option_ids
            if id != last_id
        ]

    assert len(option_ids) == 1
    winning_option = session.query(PollOption).get(option_ids[0])
    return [f'Winner: {winning_option.name}']
    # return ['Tap "vote" to rank the options by preference']

def get_ranked_options(session, poll, option_ids, users):
    option_votes = Counter({id: 0 for id in option_ids})
    for user in users:
        for vote in sorted(user.votes, key=lambda vote: vote.priority):
            print('prio', vote.poll_option_id, vote.priority)
            if vote.poll_option_id in option_ids:
                option_votes[vote.poll_option_id] += 1
                break

    return option_votes.most_common()
