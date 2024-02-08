import { Container } from 'react-bootstrap';
import Card from 'react-bootstrap/Card';
import ListGroup from 'react-bootstrap/ListGroup';
import Row from 'react-bootstrap/esm/Row';
import Col from 'react-bootstrap/esm/Col';
import QueueList from '../components/queuelist';
import QueueItem from '../components/queueitem';
import Status from '../components/status';

function Queue() {
  return (
    <div>
      <Container fluid>
        <h1 style={{textAlign: 'left', fontWeight: 'initial', marginBottom: '10px'}}>
          Queue
        </h1>
        <Row>
          <Col md={3}>
          <Status />
          </Col>
          <Col md={9}>
          <QueueList />

          
          </Col>
        </Row>

    </Container>
    </div>
    
  );
}

export default Queue;