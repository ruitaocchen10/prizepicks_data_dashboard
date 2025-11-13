-- SQLite
SELECT * FROM users LIMIT 10;

SELECT * FROM wallets LIMIT 10;

SELECT 
    u.username AS user,
    w.total_winnings AS total_winnings
FROM users u JOIN wallets w ON u.user_id = w.user_id
ORDER BY total_winnings DESC
LIMIT 10;

SELECT * FROM picks LIMIT 10;