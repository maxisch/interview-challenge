CREATE TABLE ratings (
    user_id INT NOT NULL,
    item_id INT NOT NULL,
    rating_type SMALLINT NOT NULL CHECK(rating_type BETWEEN 1 AND 3),
    CONSTRAINT pk_rating PRIMARY KEY (user_id,item_id)
);
CREATE INDEX ratings_user_id_idx ON ratings (user_id);

CREATE TABLE counts_by_rating_type (
    user_id INT NOT NULL,
    rating_type INT NOT NULL,
    count INT NOT NULL,
    CONSTRAINT pk_rating PRIMARY KEY (user_id,rating_type)
);
CREATE INDEX counts_by_rating_type_user_id_idx ON counts_by_rating_type (user_id);