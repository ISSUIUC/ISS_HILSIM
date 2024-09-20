import { Container } from 'react-bootstrap';
import Card from 'react-bootstrap/Card';
import ListGroup from 'react-bootstrap/ListGroup';
import Row from 'react-bootstrap/esm/Row';
import Col from 'react-bootstrap/esm/Col';
import QueueList from '../components/queuelist';
import Status from '../components/status';
import { useEffect, useState } from 'react';

function Queue() {

  const [refreshQueue, setRefreshQueue] = useState(false)
  const [autorefresh, setAutoRefresh] = useState(true)

  function refresh(delay) {
    setTimeout(() => {
      setRefreshQueue(!refreshQueue);
    }, delay);
  }

  useEffect(() => {
    let i = setInterval(() => {
      refresh()
    }, 1000);

    return () => {
      clearInterval(i)
    }
  }, [autorefresh])

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
          <QueueList refresh={refreshQueue}/>

          
          </Col>
        </Row>

    </Container>
    </div>
    
  );
}

export default Queue;