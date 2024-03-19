import React, { useEffect, useState } from 'react';
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
          // window.location.reload()
        }).catch((err) => {
            console.log("Couldn't submit")
        })
        props.refresh(500)
      }
    
    return <Button variant="primary" className='w-100 mb-1' onClick={() => {
        submitJob(props.repo, props.branch)
    }}>Send {props.target} job ({props.branch})</Button>
}


function TestingDashboard() {
  const [refreshQueue, setRefreshQueue] = useState(false)

  function refresh(delay) {
    setTimeout(() => {
      setRefreshQueue(!refreshQueue);
    }, delay);
  }

  useEffect(() => {
    let i = setInterval(() => {
      refresh()
    }, 1500);
  }, [])

  function dropdb() {
    console.log("(admin) attempting db drop")
    fetch(api_url.trim() + `api/admin/database`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "true"
      },
      body: JSON.stringify({})
    }).then((data) => data.json())
    .then((json_data) => {
      refresh(500)
    }).catch((err) => {
        console.log("Couldn't drop")
    })
  }

  function dropqueue() {
    console.log("(admin) attempting queue drop")
    fetch(api_url.trim() + `api/admin/queue`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "true"
      },
      body: JSON.stringify({})
    }).then((data) => data.json())
    .then((json_data) => {
      refresh(500)
    }).catch((err) => {
        console.log("Couldn't drop")
    })
  }
  
  return (
    <div>
    <NavBar />

    <Alert variant={'info'} className='m-2 p-1'>
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
                            <TestSubmitButton refresh={refresh} target={"MIDASmkI"} repo="MIDAS-Software" branch="av-1066-midas-hilsim"></TestSubmitButton>
                            <TestSubmitButton refresh={refresh} target={"TARSmkIV"} repo="TARS-Software" branch="master"></TestSubmitButton>
                        </Card.Text>
                    </Card.Body>
                </Card>
                <Card style={{textAlign: 'left', marginBottom: '10px', marginLeft: '10px'}}>
                    <Card.Body>
                        <Card.Title>System administration</Card.Title>
                        <Card.Text>
                        <Button onClick={() => {refresh()}}variant="secondary" className='w-100 mb-1'>Force queue refresh</Button>
                        <Button onClick={() => {dropdb()}}variant="danger" className='w-100 mb-1'>Clear queue</Button>
                        </Card.Text>
                    </Card.Body>
                </Card>
            </TabContainer>
        </Col>
        <Col>
            <QueueList refresh={refreshQueue} />
        </Col>
      </Row>
    </TabContainer>

    
    </div>
  );
}

export default TestingDashboard;