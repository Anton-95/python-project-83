CREATE TABLE urls (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  name varchar(255) NOT NULL,
  created_at TIMESTAMP NOT NULL
);


CREATE TABLE url_checks (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  url_id bigint NOT NULL,
  status_code integer NOT NULL,
  h1 varchar(255),
  title varchar(255),
  description varchar(255),
  created_at TIMESTAMP NOT NULL
);
