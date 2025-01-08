DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_name = 'url_checks') THEN
        EXECUTE 'DELETE FROM url_checks';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables
               WHERE table_name = 'urls') THEN
        EXECUTE 'DELETE FROM urls';
    END IF;
END $$;


CREATE TABLE IF NOT EXISTS urls (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  name varchar(255) NOT NULL,
  created_at TIMESTAMP NOT NULL
);


CREATE TABLE IF NOT EXISTS url_checks (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  url_id bigint NOT NULL,
  status_code integer NOT NULL,
  h1 varchar(255),
  title varchar(255),
  description varchar(255),
  created_at TIMESTAMP NOT NULL
);
