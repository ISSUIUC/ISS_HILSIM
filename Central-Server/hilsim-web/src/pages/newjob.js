import { Container } from "react-bootstrap";
import NavBar from "../components/common/navbar";
import NewJob from "../components/newjob";
import Row from 'react-bootstrap/esm/Row';
import Col from 'react-bootstrap/esm/Col';

function New_Job() {
    return (
        <div>
            <NavBar />
            <Container fluid className="align-items-center">
                <Row className="justify-content-center">
                    <Col md={10}>
                        <NewJob />
                    </Col>
                </Row>
            </Container>
        </div>
    );
} 

export default New_Job;