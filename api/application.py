from flask import Flask
from flask import jsonify
from flask import request
from db import connect
import json

application = Flask(__name__)


@application.route('/health')
def health():
    """
    Application's health check
    """

    return jsonify({'message': 'ok'}), 200


@application.route('/users/<user_id>/ratings/<item_id>', methods=['PUT'])
def update_rating(user_id, item_id):
    """
    Either create a new rating for a user and an item; or update the rating-type of an existing rating if any.
    Updates the counts by rating type for the user.
    Support concurrent and duplicated requests, even from the same user.
    """

    rating_type = request.get_json().get('rating_type')
    if rating_type is None or rating_type < 1 or rating_type > 3:
        return jsonify({'message': 'Error: rating type should be between 1 and 3'}), 400

    con = connect()
    cursor = con.cursor()
    query = f"""
        START TRANSACTION;

        UPDATE counts_by_rating_type
        SET count = count - 1
        WHERE counts_by_rating_type.user_id = {user_id}
            AND counts_by_rating_type.rating_type IN (
                SELECT rating_type
                FROM ratings
                WHERE user_id = {user_id} AND item_id = {item_id}
            );

        UPDATE counts_by_rating_type
        SET count = count + 1
        WHERE user_id = {user_id} AND rating_type = {rating_type};

        INSERT INTO ratings (user_id, item_id, rating_type)
        VALUES ({user_id}, {item_id}, {rating_type})
        ON DUPLICATE KEY UPDATE
            rating_type = {rating_type};
            
        COMMIT;
        """
    cursor.execute(query)
    cursor.close()
    return jsonify({'message': 'ok'}), 200


@application.route('/users/<user_id>/ratings')
def user_ratings(user_id):
    """
    List all of the ratings of a single user.
    """
    return _fetch_records(f"SELECT item_id, rating_type FROM ratings WHERE user_id = {user_id}")


@application.route('/users/<user_id>/counts')
def user_counts(user_id):
    """
    Count number of ratings per type, for a single user.
    Does not include a rating type in the list if its count is zero.
    """
    return _fetch_records(f"SELECT rating_type, count FROM counts_by_rating_type WHERE user_id = {user_id} AND count > 0")


def _fetch_records(query):
    """
    Helper private method for querying the DB
    """
    con = connect()
    cursor = con.cursor()
    cursor.execute(query)
    row_headers = [x[0] for x in cursor.description]  # this will extract row headers
    results = cursor.fetchall()
    json_data = []
    for result in results:
        json_data.append(dict(zip(row_headers, result)))
    cursor.close()
    return json.dumps(json_data)


@application.route('/users/<user_id>', methods=['DELETE'])
def user_reset(user_id):
    """
    Reset the ratings and counts of a user.
    """

    con = connect()
    cursor = con.cursor()
    cursor.execute(f"""
        START TRANSACTION;
            
        DELETE FROM ratings
        WHERE user_id = {user_id};
        
        DELETE FROM counts_by_rating_type
        WHERE user_id = {user_id};
        
        {_count_reset_query(user_id, 1)}
        {_count_reset_query(user_id, 2)}
        {_count_reset_query(user_id, 3)}
        
        COMMIT;
        """)
    cursor.close()
    return jsonify({'message': 'ok'}), 200


def _count_reset_query(user_id, rating_type):
    return f"""
            INSERT INTO counts_by_rating_type (
                user_id, rating_type, count
            )
            VALUES ({user_id}, {rating_type}, 0);
        """
