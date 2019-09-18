CREATE TEMPORARY TABLE weekdays(
    index INT,
    name VARCHAR
);

INSERT INTO weekdays (index, name) VALUES
(0, 'Sunday'),
(1, 'Monday'),
(2, 'Tuesday'),
(3, 'Wednesday'),
(4, 'Thursday'),
(5, 'Friday'),
(6, 'Saturday');


SELECT name, daily_statistic.*
    FROM daily_statistic
    JOIN weekdays on extract(dow from daily_statistic.date) = weekdays.index
ORDER By date ASC;
