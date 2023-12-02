import Button from 'react-bootstrap/Button';
import Card from 'react-bootstrap/Card';
import { Container } from 'react-bootstrap';

function QueueItem(props) {
  return (
      <Card style={{textAlign: 'left', marginBottom: '10px'}}>
      <Card.Body>
        <Card.Title>{props.username}</Card.Title>
        <Card.Text>
          {props.description}
        </Card.Text>
        <Card.Text>
          Branch: {props.branch} | Submit time {props.submit_time}
        </Card.Text>
      </Card.Body>
    </Card>
  );
}

export default QueueItem;