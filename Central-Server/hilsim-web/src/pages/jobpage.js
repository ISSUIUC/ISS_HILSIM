import React, { useEffect, useState } from 'react';
import NavBar from '../components/common/navbar';
import { Col, Row, TabContainer, Card, Alert} from 'react-bootstrap';
import { useSearchParams } from 'react-router-dom';
import { api_url } from '../dev_config';
import { KamajiJobTags } from '../components/jobtags'
import { ConsoleOutput } from '../components/consoleoutput';

function JobPage() {
    const [searchParams] = useSearchParams();
    const [output, setOutput] = useState([]);
    const [jobData, setJobData] = useState({});
    const [logData, setLogData] = useState([])
    const [waitingOutput, setWaitingOutput] = useState(false);
    

    useEffect(() => {

        function refresh() {
            let id = searchParams.get('id');

            fetch(api_url + `/api/job/${id}`, {
                headers: {
                    "ngrok-skip-browser-warning": "true",
                    "Access-Control-Allow-Origin": "*"
                }
            }).then((result) => {
                result.json().then((res_json) => {
                    setJobData(res_json);
                })
            })

            fetch(api_url + `/api/job/${id}/log`, {
                headers: {
                    "ngrok-skip-browser-warning": "true",
                    "Access-Control-Allow-Origin": "*"
                }
            }).then((result) => {
                result.text().then((res_str) => {
                    let lines = res_str.split("\n")
                    setLogData(lines)
                })
                
            }).catch((err) => {
                console.log("job log err", err)
            })

            fetch(api_url + `/api/job/${id}/data`, {
                headers: {
                    "ngrok-skip-browser-warning": "true",
                    "Access-Control-Allow-Origin": "*"
                }
            }).then((result) => {

                result.text().then((res_str) => {

                    try {
                        let json_res = JSON.parse(res_str)
                        if(json_res['error'] != undefined) {
                            setWaitingOutput(true);
                        }
                    } catch {
                        setWaitingOutput(false);
                        console.log("(job page) JSON not found, job status OK.")
                    }

                    let lines = res_str.split("\n")
                    setOutput(lines)
                })
                
            }).catch((err) => {
                console.log("job page err", err)
            })
        }

        refresh()
        let interval = setInterval(refresh, 2000); // @TODO: This is a temporary solution! 

        return () => {
            clearInterval(interval)
        }
    }, [])

    if(searchParams.get('id') == undefined) {
        return <><NavBar />
            <Alert variant={'danger'} className='m-4'>
                <b>id</b> is not defined! Check the URL of this page.
            </Alert>
            </>
    }

  let submit_time = jobData.submitted_time ? new Date(jobData.submitted_time).toLocaleString() : "";
  let begin_time = jobData.run_start ? new Date(jobData.run_start).toLocaleString() : "";
  let end_time = jobData.run_end ? new Date(jobData.run_end).toLocaleString() : "";

  return (
    <div>
        <NavBar />
        <TabContainer>
            
            <Row style={{padding: "10px"}}>
                <Col xs={3}>
                    <TabContainer className='m-2' fluid>
                        <Card style={{textAlign: 'left', marginBottom: '10px'}}>
                        <Card.Body>
                            <Card.Title className="mb-0">Job {searchParams.get('id')}</Card.Title>
                            <a className="mb-1 mt-1 text-muted" href={"https://github.com/ISSUIUC/MIDAS-Software/tree/" + jobData.branch}>{jobData.branch}</a>
                            <Card.Text className='job-data-small'>
                                Using data <a target='_blank' href={jobData.data_uri}>{jobData.data_uri}</a>
                            </Card.Text>
                            <Card.Text>
                                <KamajiJobTags status={jobData.run_status} />
                            </Card.Text>
                            <hr/>
                            <Card.Subtitle>
                                {jobData.user_id}
                            </Card.Subtitle>
                            <Card.Text className='job-data-small'>
                                Submitted {submit_time}
                            </Card.Text>
                            <Card.Text className='job-data-small'>
                                {end_time ? `Completed ${end_time}` : (jobData.run_status == "RUNNING" ? `In progress (Started ${begin_time})` : `Waiting to run`)}
                            </Card.Text>
                            <Card.Text className={"text-muted"} style={{marginTop: "5px"}}>
                                {jobData.description}
                            </Card.Text>
                            <Card.Text>Test!!</Card.Text>
                        </Card.Body>
                        </Card>
                    </TabContainer>
                </Col>
                <Col>
                    <TabContainer className='m-2' fluid>
                        <Card style={{textAlign: 'left', marginBottom: '10px'}}>
                            <Card.Body>
                                <Card.Title>Job outputs</Card.Title>
                                <Card.Subtitle className="mb-2 text-muted">Job log</Card.Subtitle>
                                <ConsoleOutput hide={false} output={logData} />
                                <Card.Subtitle className="mb-2 mt-2 text-muted">HITL output</Card.Subtitle>
                                <ConsoleOutput hide={waitingOutput} output={output} />
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