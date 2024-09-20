import Card from 'react-bootstrap/Card';
import ListGroup from 'react-bootstrap/ListGroup';
import { Container } from 'react-bootstrap';
import { useState, useEffect } from 'react';
import { api_url } from '../dev_config';
import { Link } from "react-router-dom";
import DevOnly from './devonly';
import JobItem from './jobitem';

function QueueList(props) {
  const [jobQueue, setJobQueue] = useState([]);

  useEffect(() => {
    fetch(api_url + `/api/jobs`, {headers: {
      "ngrok-skip-browser-warning": "true",
      "Access-Control-Allow-Origin": "*"
    }})
    .then(response => response.json())
    .then(json_data => {
      setJobQueue(json_data);
    }).catch((err) => {
      console.log("err fetch", err)
    })
  }, [setJobQueue, props.refresh])

  if(jobQueue.filter((job_data) => {return job_data.run_status!="SUCCESS"}).length == 0) {
    return (
      <Container fluid>
        <Card style={{textAlign: 'left', marginBottom: '10px'}}>
          <Card.Body>
            <Card.Title>The queue is empty!</Card.Title>
            <Card.Text>
              To fix that, submit a job <Link to={"/new_job"}>here!</Link>
            </Card.Text>
          </Card.Body>
        </Card>
      </Container>
    );
  }


  let allowed_job_states = ["QUEUED", "RUNNING", "SETUP_PRECOMPILE", "SETUP_COMPILING"]
  function should_show_job(job_data) {
    return allowed_job_states.includes(job_data.run_status);
  }

  return (
    <Container fluid>
      {jobQueue.map((job_data) => {
        return <><JobItem active={should_show_job(job_data)} job_data={job_data} key={job_data.run_id}/>{props.refresh}</>
      })}
    </Container>
  );
}

export default QueueList;