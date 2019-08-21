"""Module responsibel for plotting statistics."""
import io
import pandas
import matplotlib
import matplotlib.dates as mdates
import numpy as np
from sqlalchemy import func, Date, cast, Integer

from pollbot.models import User

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa


def send_plots(bot, update, session, user):
    """Generate and send plots to the user."""
    image = get_user_activity(session)
    update.message.chat.send_document(image, caption='User statistics')
    image.close()


def image_from_figure(fig):
    """Create a pillow image from a figure."""
    io_buffer = io.BytesIO()
    plt.savefig(io_buffer, format='png')
    io_buffer.seek(0)

    return io_buffer


def get_user_activity(session):
    """Create a plot showing the inline usage statistics."""
    def running_window(session, subquery):
        # Create a running window which sums all users up to this point for the current millennium ;P
        users = session.query(
            subquery.c.creation_date,
            cast(func.sum(subquery.c.count).over(
                partition_by=func.extract('millennium', subquery.c.creation_date),
                order_by=subquery.c.creation_date.asc(),
            ), Integer).label('running_total'),
        ) \
            .order_by(subquery.c.creation_date) \
            .all()

        return users

    # Grid style
    plt.style.use('seaborn-whitegrid')

    creation_date = cast(User.created_at, Date).label('creation_date')
    # Group the started users by date
    started_users_subquery = session.query(creation_date, func.count(User.id).label('count')) \
        .filter(User.started.is_(True)) \
        .group_by(creation_date) \
        .subquery()
    started_users = running_window(session, started_users_subquery)
    started_users = [('started', q[0], q[1]) for q in started_users]

    # Group the started users by date
    all_users_subquery = session.query(creation_date, func.count(User.id).label('count')) \
        .group_by(creation_date) \
        .subquery()
    all_users = running_window(session, all_users_subquery)
    all_users = [('all', q[0], q[1]) for q in all_users]

    # Group the started users by date
    voting_users_subquery = session.query(creation_date, func.count(User.id).label('count')) \
        .filter(User.votes.any()) \
        .group_by(creation_date) \
        .subquery()
    voting_users = running_window(session, voting_users_subquery)
    voting_users = [('voted', q[0], q[1]) for q in voting_users]

    # Group the started users by date
    owning_users_subquery = session.query(creation_date, func.count(User.id).label('count')) \
        .filter(User.polls.any()) \
        .group_by(creation_date) \
        .subquery()
    owning_users = running_window(session, owning_users_subquery)
    owning_users = [('currently owning poll', q[0], q[1]) for q in owning_users]

    # Combine the results in a single dataframe and name the columns
    user_statistics = started_users + all_users + voting_users + owning_users
    dataframe = pandas.DataFrame(user_statistics, columns=['type', 'date', 'users'])

    months = mdates.MonthLocator()  # every month
    months_fmt = mdates.DateFormatter('%Y-%m')

    max_number = all_users[len(all_users) - 1][2]
    # Plot each result set
    fig, ax = plt.subplots(figsize=(30, 15), dpi=120)
    for key, group in dataframe.groupby(['type']):
        ax = group.plot(ax=ax, kind='line', x='date', y='users', label=key)
        ax.xaxis.set_major_locator(months)
        ax.xaxis.set_major_formatter(months_fmt)
        ax.yaxis.set_ticks(np.arange(0, max_number, 1000))

    image = image_from_figure(fig)
    image.name = 'user_statistics.png'
    return image
