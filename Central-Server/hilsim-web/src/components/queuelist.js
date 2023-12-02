import Card from 'react-bootstrap/Card';
import ListGroup from 'react-bootstrap/ListGroup';
import QueueItem from './queueitem';
import { Container } from 'react-bootstrap';
import { useState, useEffect } from 'react';
import { api_url } from '../dev_config';
import { Link } from "react-router-dom";

function QueueList() {
  const [jobQueue, setJobQueue] = useState([]);
  useEffect(() => {
    fetch(api_url + `/api/jobs/list`, {headers: {
      "ngrok-skip-browser-warning": "true"
    }}).then((data) => {
      console.log(data)
      data.json((json_data) => {
        
        console.log(json_data)
        setJobQueue(json_data)
      }).catch((err) => {
        console.log("err", err)
      })
    }).catch((err) => {
      console.log("err", err)
    })
  }, [setJobQueue])

  if(jobQueue.length == 0) {
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

  return (
    <Container fluid>
      {jobQueue.map((job_data) => {
        <QueueItem username={job_data.username} branch={job_data.branch} description={"N/A"} submit_time={job_data.date_queue} />
      })}
    </Container>
  );
}

export default QueueList;