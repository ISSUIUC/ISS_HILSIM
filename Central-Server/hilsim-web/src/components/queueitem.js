import Button from 'react-bootstrap/Button';
import Card from 'react-bootstrap/Card';

function QueueItem() {
  return (
    <Card style={{textAlign: 'left'}}>
      <Card.Body>
        <Card.Title>Very Cool ISS Member</Card.Title>
        <Card.Text>
          Some sort of description about the job
        </Card.Text>
        <Card.Text style={{textEmphasis: 'GrayText'}}>
            when the job was submitted
        </Card.Text>
      </Card.Body>
    </Card>
  );
}

export default QueueItem;