import Button from 'react-bootstrap/Button';
import Card from 'react-bootstrap/Card';
import { Container } from 'react-bootstrap';

function QueueItem() {
  return (
      <Card style={{textAlign: 'left', marginBottom: '10px'}}>
      <Card.Body>
        <Card.Title>John Smith</Card.Title>
        <Card.Text>
          Testing midas code
        </Card.Text>
        <Card.Text>
          Branch: AV-1045
        </Card.Text>
        <Card.Text style={{textEmphasis: 'GrayText'}}>
            Submitted at 10:15am
        </Card.Text>
      </Card.Body>
    </Card>
  );
}

export default QueueItem;