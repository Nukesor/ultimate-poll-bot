from pollbot.models import Vote, User, PollOption
from sqlalchemy import func
from collections import Counter

def get_stv_result(session, poll):
    # todo this query fetches all votes for the user, not only those belonging to the current poll
    users = session.query(User) \
        .join(User.votes) \
        .filter(Vote.poll_id == poll.id) \
        .all()

    lines = []

    lines.append('\nSTV Tally:')
    option_ids = [option.id for option in poll.options]
    print('init ids', option_ids)
    for _ in range(len(option_ids) - 1):
        if (len(option_ids) <= 1):
            winning_option = session.query(PollOption).get(option_ids[0])
            lines.append(f'STV Winner: {winning_option.name}')
            break

        ranked_options = get_ranked_options(session, poll, option_ids, users)
        print('ranked', ranked_options)
        last_id, last_rank = ranked_options[-1]
        options_with_same_rank = [
            id for id, rank in ranked_options
            if rank == last_rank and id != last_id
        ]

        if (len(options_with_same_rank) > 0):
            names = ', '.join([
                session.query(PollOption).get(id).name
                for id in options_with_same_rank + [last_id]
            ])
            lines.append(f'{names} all have the least amount of votes, couldnt decide which to kick out.')
            break

        option_ids = [
            id for id in option_ids
            if id != last_id
        ]

    lines.append('\nBorda count tally:')
    lines.extend(get_borda_count_lines(session, poll))

    return lines

def get_ranked_options(session, poll, option_ids, users):
    option_votes = Counter({id: 0 for id in option_ids})
    for user in users:
        print('vote count', len(user.votes))
        for vote in sorted(user.votes, key=lambda vote: vote.priority):
            print('option prio', vote.poll_option_id, vote.priority)
            if vote.poll_option_id in option_ids:
                option_votes[vote.poll_option_id] += 1
                break

    return option_votes.most_common()

def get_borda_count_lines(session, poll):
    option_count = len(poll.options)
    counter = Counter({option: 0 for option in poll.options})
    for option in poll.options:
        counter[option] += sum([option_count - vote.priority for vote in option.votes])
    return [f'{option.name}: {points} Points' for option, points in counter.most_common()]
