# Queries

## Stats by Weekday

```sql
CREATE TEMPORARY TABLE weekdays(
    index INT,
    name VARCHAR
);

INSERT INTO weekdays (index, name) VALUES
(0, 'Monday'),
(1, 'Tuesday'),
(2, 'Wednesday'),
(3, 'Thursday'),
(4, 'Friday'),
(5, 'Saturday'),
(6, 'Sunday');


SELECT name, daily_statistic.*
    FROM daily_statistic
    JOIN weekdays on extract(dow from daily_statistic.date) = weekdays.index
ORDER By date ASC;
```

## Vote with Poll

```sql
SELECT p.id, p.name, p.poll_type, o.name, v.id, v.type
    FROM poll AS p
    JOIN vote AS v ON poll.id = vote.poll_id
    JOIN option AS o ON vote.option_id = option.id
WHERE p.created IS TRUE ORDER BY p.id, o.id DESC limit 200;
#WHERE p.id = :number;
```

## Biggest polls

```sql
SELECT p.id, SUM(v.vote_count), COUNT(DISTINCT(u.id)), p.created_at, p.name, p.poll_type
FROM poll as p
JOIN vote as v ON v.poll_id = p.id
JOIN "user" as u ON u.id = v.user_id
GROUP BY p.id, p.created_at, p.name, p.poll_type
ORDER BY SUM(v.vote_count) DESC
LIMIT 400;
```

## Show options of poll

```sql
SELECT o.name, o.description
FROM option AS o
JOIN poll AS p ON o.poll_id = p.id
WHERE p.id = :poll_id;
```
