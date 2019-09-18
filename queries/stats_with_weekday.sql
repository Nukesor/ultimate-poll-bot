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
