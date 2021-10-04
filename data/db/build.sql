CREATE TABLE IF NOT EXISTS Course  (
	course_id INTEGER PRIMARY KEY,
	course_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Module (
	module_id INTEGER PRIMARY KEY,
	course_id INTEGER,
	module_name TEXT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES Course(course_id)
);

CREATE TABLE IF NOT EXISTS File (
	file_id INTEGER PRIMARY KEY,
	course_id INTEGER DEFAULT NULL,
	module_id INTEGER DEFAULT NULL,
	filename TEXT NOT NULL,
	display_name TEXT NOT NULL,
	content_type TEXT NOT NULL,
	url TEXT NOT NULL,
	updated_at TEXT NOT NULL,    -- https://www.sqlite.org/datatype3.html#date_and_time_datatype
	modified_at TEXT NOT NULL,   -- https://www.sqlite.org/datatype3.html#date_and_time_datatype
    -- Only updated_at or modified_at is needed don't know which at this point
    downloaded_at TEXT DEFAULT NULL,
    FOREIGN KEY (course_id) REFERENCES Course(course_id)
    FOREIGN KEY (module_id) REFERENCES Module(module_id)
);
