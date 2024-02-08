import React from 'react';
import NavBar from '../components/common/navbar';
import QueueList from '../components/queuelist';
import { api_url } from '../dev_config';
import { Alert, Col, Row, TabContainer, Card, Button } from 'react-bootstrap';

function TestSubmitButton(props) {
    
    function submitJob(avionicsRepo, selectedBranch) {
        fetch(api_url + `/api/job`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "ngrok-skip-browser-warning": "true",
            "Access-Control-Allow-Origin": "*"
          },
          body: JSON.stringify({
            commit: "0000",
            username: "hilsim-testingdashboard",
            branch: selectedBranch,
            description: "Invoked from testing dashboard"
          })
        }).then((data) => data.json())
        .then((json_data) => {
          // Reload the page on success (to update queue)
          window.location.reload()
        }).catch((err) => {
            console.log("Couldn't submit")
        })
      }
    
    return <Button variant="primary" className='w-100 mb-1' onClick={() => {
        submitJob(props.repo, props.branch)
    }}>Send {props.target} job ({props.branch})</Button>
}


function TestingDashboard() {
  return (
    <div>
    <NavBar />

    <Alert variant={'warning'} className='m-2 p-1'>
          This page is only visible on the Kamaji Development environment. 
    </Alert>

    <TabContainer>
      <Row>
        <Col xs={4}>
            <TabContainer fluid>
                <Card style={{textAlign: 'left', marginBottom: '10px', marginLeft: '10px'}}>
                    <Card.Body>
                        <Card.Title>Quick job submission</Card.Title>
                        <Card.Text>
                            <TestSubmitButton target={"MIDASmkI"} repo="MIDAS-Software" branch="av-1066-midas-hilsim"></TestSubmitButton>
                            <TestSubmitButton target={"TARSmkIV"} repo="TARS-Software" branch="master"></TestSubmitButton>
                        </Card.Text>
                    </Card.Body>
                </Card>
                <Card style={{textAlign: 'left', marginBottom: '10px', marginLeft: '10px'}}>
                    <Card.Body>
                        <Card.Title>System administration</Card.Title>
                        <Card.Text>
                            <Button variant="secondary" className='w-100 mb-1'>Refresh queue</Button>
                            <Button variant="warning" className='w-100 mb-1'>Clear queue</Button>
                            <Button variant="danger" className='w-100 mb-1'>Clear database</Button>
                        </Card.Text>
                    </Card.Body>
                </Card>
            </TabContainer>
        </Col>
        <Col>
            <QueueList />
        </Col>
      </Row>
    </TabContainer>

    
    </div>
  );
}

export default TestingDashboard;