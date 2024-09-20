import Card from 'react-bootstrap/Card';
import ListGroup from 'react-bootstrap/ListGroup';
import { Container } from 'react-bootstrap';
import { useState, useEffect } from 'react';
import { api_url } from '../dev_config';
import { Link } from "react-router-dom";
import JobItem from './jobitem';

function JobList() {
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
  }, [setJobQueue])

  if(jobQueue.length == 0) {
    return (
      <Container fluid>
        <Card style={{textAlign: 'left', marginBottom: '10px'}}>
          <Card.Body>
            <Card.Title>There are no Jobs!</Card.Title>
            <Card.Text>
              To fix that, submit a job <Link to={"/new_job"}>here!</Link>
            </Card.Text>
          </Card.Body>
        </Card>
      </Container>
    );
  }


  return (
    <Container fluid>
      {jobQueue.filter((job_data) => job_data.run_status=="RUNNING").map((job_data) => {
        return <JobItem active job_data={job_data} key={job_data.run_id}/>
      })}
      {jobQueue.filter((job_data) => job_data.run_status=="QUEUED").map((job_data) => {
        return <JobItem active job_data={job_data} key={job_data.run_id}/>
      })}
      {jobQueue.filter((job_data) => job_data.run_status=="SUCCESS").map((job_data) => {
        return <JobItem active job_data={job_data} key={job_data.run_id}/>
      })}
    </Container>
  );
}

export default JobList;