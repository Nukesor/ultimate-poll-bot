SELECT p.id, p.name, p.poll_type, o.name, v.id, v.type
    FROM poll AS p
    JOIN vote AS v ON poll.id = vote.poll_id
    JOIN poll_option AS o ON vote.poll_option_id = poll_option.id
WHERE p.created IS TRUE ORDER BY p.id, o.id DESC limit 200

# WHERE p.id = :number;
