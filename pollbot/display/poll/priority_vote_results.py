from collections import Counter
from typing import List, Tuple

from sqlalchemy.orm.scoping import scoped_session

from pollbot.models import Option, Poll, User, Vote


# this is not used at the moment, but maybe we'd like to add this feature later
def get_priority_result(session: scoped_session, poll: Poll) -> List[str]:
    # todo this query fetches all votes for the user, not only those belonging to the current poll
    users = session.query(User).join(User.votes).filter(Vote.poll_id == poll.id).all()

    lines = []

    lines.append("\nPriority Tally:")
    option_ids = [option.id for option in poll.options]
    for _ in range(len(option_ids) - 1):
        if len(option_ids) <= 1:
            winning_option = session.query(Option).get(option_ids[0])
            lines.append(f"Priority Winner: {winning_option.name}")
            break

        ranked_options = get_ranked_options(option_ids, users)
        last_id, last_rank = ranked_options[-1]
        options_with_same_rank = [
            id for id, rank in ranked_options if rank == last_rank and id != last_id
        ]

        if len(options_with_same_rank) > 0:
            names = ", ".join(
                [
                    session.query(Option).get(id).name
                    for id in options_with_same_rank + [last_id]
                ]
            )
            lines.append(
                f"{names} all have the least amount of votes, couldnt decide which to kick out."
            )
            break

        option_ids = [id for id in option_ids if id != last_id]

    return lines


def get_ranked_options(
    option_ids: List[int], users: List[User]
) -> List[Tuple[int, int]]:
    option_votes = Counter({id: 0 for id in option_ids})
    for user in users:
        for vote in sorted(user.votes, key=lambda vote: vote.priority):
            if vote.option_id in option_ids:
                option_votes[vote.option_id] += 1
                break

    return option_votes.most_common()
