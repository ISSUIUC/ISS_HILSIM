import React, { useEffect, useState } from 'react';
import NavBar from '../components/common/navbar';
import QueueList from '../components/queuelist';
import { Col, Row, TabContainer, Card, Alert} from 'react-bootstrap';
import { useSearchParams } from 'react-router-dom';
import { api_url } from '../dev_config';
import { KamajiJobTags, KamajiTag } from '../components/jobtags'

function ConsoleOutputLine(props) {
    let padding = props.linePadding - (props.index.toString().length)
    // Pad using the unicode nbsp character, "\u00A0", NOT a regular space.
    return <span>
        <span className={'console-output-line' + (props.blur ? " blurred-text-gray" : "")}>{"\u00A0".repeat(padding) + props.index.toString()} |</span><span className={props.blur ? " blurred-text" : ""}> {props.text}</span>
    </span> 
}

function JobRawOutput(props) {

    const [expanded, setExpanded] = useState(false)

    let output = props.hide ? ["There is no spoon!","You are worthy of great things :)","You should be proud of yourself.","Be patient, this too shall pass.","You are loved <3"] : props.output

    return (<Card className={"card-output"}>
        <Card variant={"top"} className={(expanded ? "" : "job-raw-output-container ") + "bg-dark text-white code-text" + (props.hide ? " user-select-none" : "")} style={{textAlign: 'left', padding: '5px'}}>
            {output.map((str, lineIndex) => {
                return <ConsoleOutputLine blur={props.hide} linePadding={props.lineNumWidth} index={lineIndex+1} text={str} />
            })}
            <br/>
            <span className={'console-output-line' + (props.hide ? " blurred-text-gray" : "")}>( EOF )</span>


        </Card>
        <div className={'no-job-raw-output'  + (!props.hide ? " d-none" : "")}>
            This job does not have any output yet.
        </div>
        <div className={'extend-job-raw-output' + (props.hide ? " d-none" : "")} onClick={() => {setExpanded(!expanded)}}>
            {expanded ? "▲" : "▼"}
        </div>
    </Card>);
}

function JobPage() {
    const [searchParams] = useSearchParams();
    const [output, setOutput] = useState([]);
    const [jobData, setJobData] = useState({});
    const [lineNumWidth, setLineNumWidth] = useState(0);
    const [waitingOutput, setWaitingOutput] = useState(false);
    

    useEffect(() => {
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
                setLineNumWidth(lines.length.toString().length)
                setOutput(lines)
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
                            <Card.Title>Job {searchParams.get('id')}</Card.Title>
                            <Card.Subtitle className="mb-1 text-muted">{jobData.branch}</Card.Subtitle>
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
                        </Card.Body>
                        </Card>
                    </TabContainer>
                </Col>
                <Col>
                    <TabContainer className='m-2' fluid>
                        <Card style={{textAlign: 'left', marginBottom: '10px'}}>
                            <Card.Body>
                                <Card.Title>HITL Simulation outputs</Card.Title>
                                <Card.Subtitle className="mb-2 text-muted">HITL output</Card.Subtitle>
                                <JobRawOutput hide={waitingOutput} output={output} lineNumWidth={lineNumWidth} />
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