CREATE TABLE users (
	user_id	 SERIAL,
	username VARCHAR(512) NOT NULL,
	email	 VARCHAR(512) NOT NULL,
	password VARCHAR(512) NOT NULL,
	PRIMARY KEY(user_id)
);

CREATE TABLE auctions (
	auction_id	 SERIAL,
	item_name	 VARCHAR(512) NOT NULL,
	end_date_time TIMESTAMP NOT NULL,
	min_price	 FLOAT(8) NOT NULL,
	users_user_id INTEGER NOT NULL,
	PRIMARY KEY(auction_id)
);

CREATE TABLE bids (
	bid_id		 SERIAL,
	amount		 FLOAT(8) NOT NULL,
	users_user_id	 INTEGER NOT NULL,
	auctions_auction_id INTEGER NOT NULL,
	PRIMARY KEY(bid_id)
);

CREATE TABLE comments (
	comment_id		 SERIAL,
	comm_content	 VARCHAR(512) NOT NULL,
	users_user_id	 INTEGER NOT NULL,
	auctions_auction_id INTEGER NOT NULL,
	PRIMARY KEY(comment_id)
);

CREATE TABLE notifications (
	notif_id	 SERIAL,
	notif_content VARCHAR(512) NOT NULL,
	users_user_id INTEGER NOT NULL,
	PRIMARY KEY(notif_id)
);

CREATE TABLE tokens (
	token_id	 SERIAL,
	token	 VARCHAR(512) NOT NULL,
	exp_date TIMESTAMP NOT NULL,
	users_user_id INTEGER NOT NULL,
	PRIMARY KEY(token_id)
);

ALTER TABLE users ADD UNIQUE (username, email);
ALTER TABLE auctions ADD CONSTRAINT auctions_fk1 FOREIGN KEY (users_user_id) REFERENCES users(user_id);
ALTER TABLE bids ADD CONSTRAINT bids_fk1 FOREIGN KEY (users_user_id) REFERENCES users(user_id);
ALTER TABLE bids ADD CONSTRAINT bids_fk2 FOREIGN KEY (auctions_auction_id) REFERENCES auctions(auction_id);
ALTER TABLE comments ADD CONSTRAINT comments_fk1 FOREIGN KEY (users_user_id) REFERENCES users(user_id);
ALTER TABLE comments ADD CONSTRAINT comments_fk2 FOREIGN KEY (auctions_auction_id) REFERENCES auctions(auction_id);
ALTER TABLE notifications ADD CONSTRAINT notifications_fk1 FOREIGN KEY (users_user_id) REFERENCES users(user_id);
ALTER TABLE tokens ADD UNIQUE (token);
ALTER TABLE tokens ADD CONSTRAINT tokens_fk1 FOREIGN KEY (users_user_id) REFERENCES users(user_id);
