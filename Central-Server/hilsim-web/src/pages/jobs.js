import { Container } from 'react-bootstrap';
import Card from 'react-bootstrap/Card';
import ListGroup from 'react-bootstrap/ListGroup';
import Row from 'react-bootstrap/esm/Row';
import Col from 'react-bootstrap/esm/Col';
import JobList from '../components/joblist';
import QueueItem from '../components/queueitem';
import Status from '../components/status';
import NavBar from '../components/common/navbar';

function Jobs() {
  return (
    <div>
      
        <NavBar/>
      <Container fluid>
        <h1 style={{textAlign: 'left', fontWeight: 'initial', marginBottom: '10px'}}>
          Jobs
        </h1>
        <Row>
          <Col md={3}>
          <Status />
          </Col>
          <Col md={9}>
          <JobList />
          </Col>
        </Row>
    </Container>
    </div>
    
  );
}

export default Jobs;