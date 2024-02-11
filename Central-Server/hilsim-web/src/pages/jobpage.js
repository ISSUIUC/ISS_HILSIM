import React, { useEffect, useState } from 'react';
import NavBar from '../components/common/navbar';
import QueueList from '../components/queuelist';
import { Col, Row, TabContainer, Card, Alert } from 'react-bootstrap';
import { useSearchParams } from 'react-router-dom';
import { api_url } from '../dev_config';


function JobPage() {
    const [searchParams] = useSearchParams();
    const [output, setOutput] = useState("");
    

    useEffect(() => {
        let id = searchParams.get('id');
        fetch(api_url + `/api/job/${id}/data`, {
            headers: {
                "ngrok-skip-browser-warning": "true",
                "Access-Control-Allow-Origin": "*"
              }
        }).then((result) => {
            result.text().then((res_str) => {
                setOutput(res_str)
            })
            
        }).catch((err) => {
            console.log("job page err", err)
        })

    }, [searchParams])

    if(searchParams.get('id') == undefined) {
        return <><NavBar />
            <Alert variant={'danger'} className='m-4'>
                <b>id</b> is not defined! Check the URL of this page.
            </Alert>
            </>
    }

  return (
    <div>
        <NavBar />
        <TabContainer>
            
            <Row style={{padding: "10px"}}>
                <Col xs={3}>
                    <TabContainer className='m-2' fluid>
                        <Card style={{textAlign: 'left', marginBottom: '10px'}}>
                        <Card.Body>
                            <Card.Title>Job overview</Card.Title>
                            <Card.Text>
                                WE R DEAD 💀💀💀💀
                            </Card.Text>
                        </Card.Body>
                        </Card>
                    </TabContainer>
                </Col>
                <Col>
                    <TabContainer className='m-2' fluid>
                            <Card style={{textAlign: 'left', marginBottom: '10px'}}>
                                <Card.Body>
                                    <Card.Title>HITL Simulation outputs</Card.Title>
                                    <Card.Subtitle className="mb-2 text-muted">Raw output</Card.Subtitle>
                                    <Card.Text>
                                        <Card className="bg-dark text-white code-text" style={{textAlign: 'left', padding: '5px'}}>
                                            {output}
                                        </Card>
                                        
                                    </Card.Text>
                                </Card.Body>
                            </Card>
                    </TabContainer>
                </Col>
            </Row>
        </TabContainer>
    </div>
  );
}

export default JobPage;