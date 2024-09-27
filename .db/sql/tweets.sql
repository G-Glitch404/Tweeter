CREATE TABLE IF NOT EXISTS "tweets"(
	"id" INTEGER,
	"post_type" TEXT NOT NULL,
	"text_body"	TEXT,
	"media_file_path"	TEXT,
	"upload_date"	TEXT,
	"bot_username"	TEXT NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
