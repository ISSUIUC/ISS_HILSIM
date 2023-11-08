import Button from 'react-bootstrap/Button';
import Card from 'react-bootstrap/Card';

function Status() {
  return (
    <Card style={{textAlign: 'left'}}>
      <Card.Body>
        <Card.Title>Server Status</Card.Title>
        <Card.Text style={{fontWeight: 'bold'}}>
          Server 1 - Ballin
        </Card.Text>
        <Card.Text style={{fontWeight: 'bold'}}>
            Server 2 - Trappin
        </Card.Text>
        <Card.Text style={{fontWeight: 'bold'}}>
            Server 3 - Aliv
        </Card.Text>
      </Card.Body>
    </Card>
  );
}

export default Status;