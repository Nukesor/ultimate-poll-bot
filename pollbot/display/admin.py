from pollbot.models import Poll, User


def stats(session):
    """Get user stats."""
    # User stats
    total_users = session.query(User.id).count()
    users_owning_polls = (
        session.query(User)
        .join(User.polls)
        .filter(Poll.created.is_(True))
        .group_by(User)
        .count()
    )
    users_with_votes = session.query(User).join(User.votes).group_by(User).count()
    users_started = session.query(User).filter(User.started.is_(True)).count()

    # Polls
    highest_id = session.query(Poll.id).order_by(Poll.id.desc()).first()[0]
    total_polls = session.query(Poll).filter(Poll.delete.is_(None)).count()
    created_polls = (
        session.query(Poll)
        .filter(Poll.closed.is_(False))
        .filter(Poll.created.is_(True))
        .filter(Poll.delete.is_(None))
        .count()
    )
    unfinished_polls = (
        session.query(Poll)
        .filter(Poll.closed.is_(False))
        .filter(Poll.created.is_(False))
        .filter(Poll.delete.is_(None))
        .count()
    )

    closed_polls = (
        session.query(Poll)
        .filter(Poll.closed.is_(True))
        .filter(Poll.delete.is_(None))
        .count()
    )

    # Poll types
    single = session.query(Poll).filter(Poll.poll_type == "single_vote").count()
    doodle = session.query(Poll).filter(Poll.poll_type == "doodle").count()
    count = session.query(Poll).filter(Poll.poll_type == "count_vote").count()
    priority = session.query(Poll).filter(Poll.poll_type == "priority").count()
    block = session.query(Poll).filter(Poll.poll_type == "block_vote").count()
    limited = session.query(Poll).filter(Poll.poll_type == "limited_vote").count()
    cumulative = session.query(Poll).filter(Poll.poll_type == "cumulative_vote").count()
    to_be_deleted = session.query(Poll).filter(Poll.delete.isnot(None)).count()

    single_percent = single / total_polls * 100
    doodle_percent = doodle / total_polls * 100
    count_percent = count / total_polls * 100
    priority_percent = priority / total_polls * 100
    block_percent = block / total_polls * 100
    limited_percent = limited / total_polls * 100
    cumulative_percent = cumulative / total_polls * 100

    message = f"""Users:
    Total: {total_users}
    Started: {users_started}
    Owning polls: {users_owning_polls}
    Voted: {users_with_votes}

Polls:
    Highest ID: {highest_id}
    Total: {total_polls}
    Open: {created_polls}
    Unfinished: {unfinished_polls}
    Closed: {closed_polls}
    Deleted: {highest_id - total_polls}
    To be deleted: {to_be_deleted}

Types:
    Single:  {single} ({single_percent:.2f}%)
    Doodle: {doodle} ({doodle_percent:.2f}%)
    Count: {count} ({count_percent:.2f}%)
    Priority: {priority} ({priority_percent:.2f}%)
    Block: {block} ({block_percent:.2f}%)
    Limited: {limited} ({limited_percent:.2f}%)
    Cumulative: {cumulative} ({cumulative_percent:.2f}%)
"""

    return message
