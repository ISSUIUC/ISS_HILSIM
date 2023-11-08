import Card from 'react-bootstrap/Card';
import ListGroup from 'react-bootstrap/ListGroup';
import QueueItem from './queueitem';
import { Container } from 'react-bootstrap';

function QueueList() {
  return (
    <Container fluid>
      <QueueItem />
      <QueueItem />
      <QueueItem />
      <QueueItem />
      <QueueItem />
    </Container>
  );
}

export default QueueList;