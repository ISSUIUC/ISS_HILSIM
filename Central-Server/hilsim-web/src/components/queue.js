import { Container } from 'react-bootstrap';
import Card from 'react-bootstrap/Card';
import ListGroup from 'react-bootstrap/ListGroup';
import Row from 'react-bootstrap/esm/Row';
import Col from 'react-bootstrap/esm/Col';
import QueueList from './queuelist';
import QueueItem from './queueitem';
import Status from './status';
import NewJob from './newjob';

function Queue() {
  return (
    <Container fluid>
        <h1 style={{textAlign: 'left'}}>
          Queue
        </h1>
        <Row>
          <Col md={3}>
          <Status />
          </Col>
          <Col md={9}>
          <NewJob />
          <br />
          <QueueList />
          </Col>
        </Row>
    </Container>
    
  );
}

export default Queue;