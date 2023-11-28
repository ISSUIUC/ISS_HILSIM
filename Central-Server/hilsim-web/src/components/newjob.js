import Button from 'react-bootstrap/Button';
import Card from 'react-bootstrap/Card';
import Row from 'react-bootstrap/esm/Row';
import Col from 'react-bootstrap/esm/Col';
import { Form } from 'react-bootstrap';


function NewJob() {
  return (
    <Card style={{textAlign: 'left', marginTop: '20px'}}>
      <Card.Header style={{fontWeight: 'bold', textAlign: 'left'}}>Submit Job</Card.Header>
      <Card.Body>
      <Form>
      <Form.Group as={Row} className="mb-3" controlId="formHorizontalEmail">
        <Form.Label column sm={2}>
          Email/User
        </Form.Label>
        <Col sm={10}>
          <Form.Control disabled readonly type="email" placeholder=" * This field will be automatically filled in *" />
        </Col>
      </Form.Group>

      <Form.Group as={Row} className="mb-3" controlId="jobDescription">
        <Form.Label column sm={2}>
          Description
        </Form.Label>
        <Col sm={10}>
          <Form.Control as="textarea" rows={3} placeholder="Something about the job idk" />
        </Col>
      </Form.Group>

      <Form.Group as={Row} className="mb-3">
        <Form.Label column sm={2}>Select Branch</Form.Label>
        <Col sm={10}>
          <Form.Select aria-label="Default select example">
            <option>Choose a brach to run</option>
            <option value="1">AV-1044</option>
            <option value="2">AV-1045</option>
            <option value="3">AV-1046</option>
        </Form.Select>
        </Col> 
      </Form.Group>

      <Form.Group as={Row} className="mb-3">
        <Col sm={{ span: 10, offset: 2 }}>
          <Button type="submit">Submit</Button>
        </Col>
      </Form.Group>
    </Form>
      </Card.Body>
    </Card>
  );
}

export default NewJob;