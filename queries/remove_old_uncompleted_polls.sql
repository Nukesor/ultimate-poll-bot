DELETE FROM "poll" as p1
    WHERE created = False
    AND EXISTS (
        SELECT * from poll as p2
            WHERE p2.created = false
            AND p2.created_at > p1.created_at
            AND p1.user_id = p2.user_id
        )
