from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json_encoder.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        # fetch all messages ordered by created_at in ascending order
        messages = Message.query.order_by(Message.created_at.asc()).all()
        # serialize messages to JSON
        messages_json = [message.to_dict() for message in messages]
        response = jsonify(messages_json), 200
        return response

    elif request.method == 'POST':
        # extract data from request parameters
        body = request.json.get('body')
        username = request.json.get('username')

        # create a new message
        new_message = Message(body=body, username=username)
        db.session.add(new_message)
        db.session.commit()

        response = jsonify(new_message.to_dict()), 201
        
        return response


@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    # find the messages by id
    message = Message.query.get(id)
    if not message:
        return jsonify({'error': 'message not found'}), 404
    
    # update message body if provided in request params
    if 'body' in request.json:
        message.body = request.json['body']

    db.session.commit()

    # return the updated message as JSON
    return jsonify(message.to_dict())

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    # find message by id
    message = Message.query.get(id)
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    db.session.delete(message)
    db.session.commit()

    return jsonify({'message': 'message deleted successfully'}), 200

if __name__ == '__main__':
    app.run(port=5555, debug=True)
